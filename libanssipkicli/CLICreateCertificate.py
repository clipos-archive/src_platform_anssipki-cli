# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import os
import sys
import argparse
import re
import ConfigParser
import subprocess
import logging

from libanssipki import anssipki
from libanssipki.Conf import Conf
from libanssipki.CSR import CSR
from libanssipki.CACertificate import CACertificate
from libanssipki.Certificate import Certificate
from libanssipki.DBHelper import DBHelper
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName, parseValidity, createArgumentParser
from libanssipkicli import _

def parseKeyAlgo(string):
	try:
		return anssipki.keyPairAlgoFromStr(string)
	except Exception, e:
		raise Exception(_("CLI_INVALID_KEY_ALGO") % string)

def parseSignAlgo(string):
	if anssipki.SignAlgoStrToP11Mech(string) == 0:
		raise Exception(_("CLI_INVALID_SIGN_ALGO") % string)
	return string


def parseKeyUsage(string):
	res = set()
	for ku in string.split(':'):
		try:
			res.add(anssipki.keyUsageFromStr(ku))
		except Exception, e:
			raise Exception(_("CLI_INVALID_KU") % ku)
	if len(res) == 0: raise Exception(_("CLI_INVALID_KU") % string)
	return res

def parseExtendedKeyUsage(string):
	res = set()
	for ku in string.split(':'):
		try:
			res.add(anssipki.extendedKeyUsageFromStr(ku))
		except Exception, e:
			raise Exception(_("CLI_INVALID_EKU") % ku)
	if len(res) == 0: raise Exception(_("CLI_INVALID_EKU") % string)
	return res

def parseSAN(string):
	try:
		san,sep,value = string.partition(":")
		san = san.lower()
		try:
			return anssipki.SANFromStr(san), value
		except Exception, e:
			raise Exception(_("CLI_INVALID_SAN") % san)
	except ValueError, e:
		raise Exception(_("CLI_INVALID_SAN") % string)

def parseCertPolicy(string):
	#FIXME add regex check
	policies = {}
	for pol in string.split("|"):
		oid, sep, cps = pol.partition(":")
		if oid in policies:
			raise Exception(_("CLI_CERT_POL_OID_REDEFINITION"))
		policies[oid] = cps
	return policies

class CLICreateCertificate(CLIAction):
	actions = ["createca", "createsubca", "createcert"]

	def __init__(self, action):
		super(CLICreateCertificate, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--template", action=UniqueAppendAction,
								help=_("CLI_CREATE_CERT_TEMPLATE_HELP")),
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--validity", type=parseValidity, action=UniqueAppendAction,
								help=_("CLI_VALIDITY_OPTION_HELP"))
		self.parser.add_argument("--keysize", type=int, action=UniqueAppendAction,
								help=_("CLI_KEYSIZE_OPTION_HELP")),
		self.parser.add_argument("--keyalgo", type=parseKeyAlgo, action=UniqueAppendAction,
								help=_("CLI_KEYALGO_OPTION_HELP")),
		self.parser.add_argument("--signalgo", type=parseSignAlgo, action=UniqueAppendAction,
								help=_("CLI_SIGNALGO_OPTION_HELP")),
		if action == "createsubca" or action == "createcert":
			self.parser.add_argument("--issuerdn", type=parseDN, action=UniqueAppendAction,
									help=_("CLI_ISSUERDN_OPTION_HELP")),
		if action == "createcert":
			self.parser.add_argument("--smartcard",  default=False, action='store_true',
									help=_("CLI_SMARTCARD_OPTION_HELP"))
			self.parser.add_argument("--selfsigned", default=False, action='store_true',
									help=_("CLI_SELFSIGNED_OPTION_HELP")),
			self.parser.add_argument("--keyusage", type=parseKeyUsage, action=UniqueAppendAction,
									help=_("CLI_KU_OPTION_HELP")),
			self.parser.add_argument("--extkeyusage",  type=parseExtendedKeyUsage, action=UniqueAppendAction,
									help=_("CLI_EKU_OPTION_HELP"))
			self.parser.add_argument("--san", type=parseSAN, action='append',
									help=_("CLI_SAN_OPTION_HELP"))
			self.parser.add_argument("--OSSLextension",  type=str, action='append',
									help=_("CLI_OSSLEXT_OPTION_HELP"))
		self.parser.add_argument("--certpolicies",  type=parseCertPolicy, action=UniqueAppendAction,
								help=_("CLI_CERTPOL_OPTION_HELP"))

	@staticmethod
	def usage():
		print "\t"  + "createca: " + _("CLI_CREATECA_USAGE")
		print "\t"  + "createsubca: " + _("CLI_CREATESUBCA_USAGE")
		print "\t"  + "createcert: " + _("CLI_CREATECERT_USAGE")

	def parseTemplate(self, filename, parser, oldargs):
		template_filepath = None
		for template_dir in Conf.getValue("TEMPLATES_DIR"):
			if os.path.exists(template_dir + "/" + filename + ".tpl"):
				template_filepath = template_dir + "/" + filename + ".tpl"
		if not template_filepath:
			raise Exception(_("CLI_TEMPLATE_NOT_FOUND_ERROR") % filename)
		args = []
		template = ConfigParser.ConfigParser()
		with open(template_filepath, "r") as fp:
			template.readfp(fp)
		if 'PARENT' in template.sections():
			for (i,v) in template.items('PARENT'):
				if i != 'template':
					raise Exception("%s: Invalid key in PARENT section." % filename)
				oldargs = self.parseTemplate(v, parser, oldargs)
				# Autorise les templates avec juste une section PARENT, sorte de template 'alias'
				if 'CERTIFICATE' not in template.sections():
					return args
		else:
			if 'CERTIFICATE' not in template.sections():
				raise Exception("Can't find group [CERTIFICATE] in template file : %s" % filename)
		for (i,v) in template.items('CERTIFICATE'):
			override = False
			for arg in sys.argv:
				if arg.find("--"+i) == 0:
					override = True
					break
			if not override:
				args.append("--"+i+"="+v)
		return parser.parse_args(args, oldargs)

	def do(self, args):
		args = self.parser.parse_args(args)

		createCA = self.action == 'createca'
		createSubCA = self.action == 'createsubca'
		createCert = self.action == 'createcert'
		selfsigned = False
		useSmartcard = False
		sanOpt = None
		osslExtOpt = None
		if createCA:
			selfsigned = True
		if createSubCA:
			selfsigned = False
		if createCert:
			selfsigned = args.selfsigned
			useSmartcard = args.smartcard
			sanOpt = args.san
			osslExtOpt = args.OSSLextension



		if args.template:
			args = self.parseTemplate(args.template, self.parser, args)

		if args.dn == None:
			raise Exception(_("CLI_DN_NOT_SET_ERROR"))
		if args.validity == None:
			raise Exception(_("CLI_VALIDITY_NOT_SET_ERROR"))
		if createCert and args.keyusage == None:
			raise Exception(_("CLI_KU_NOT_SET_ERROR"))
		if (selfsigned or createCA) and args.signalgo == None:
			raise Exception(_("CLI_SA_NOT_SET_ERROR"))
		if createCert and selfsigned and args.issuerdn != None:
			raise Exception(_("CLI_ISSUER_AND_SS_SET_ERROR"))
		if not createCA and not selfsigned and args.issuerdn == None:
			raise Exception(_("CLI_NO_ISSUER_SET_ERROR"))
		if args.keysize == None:
			raise Exception(_("CLI_KS_NOT_SET_ERROR"))
		if args.keyalgo == None:
			raise Exception(_("CLI_KA_NOT_SET_ERROR"))
		if createCert and anssipki.KeyCertSign in args.keyusage:
			raise Exception(_("CLI_CREATECERT_KCS_KU_SET_ERROR"))

		if DBHelper.getInstance().getCertificateFromDN(args.dn) != None:
			raise Exception(_("CLI_CERT_DN_ALREADY_EXISTS") % args.dn)

		csr = CSR(args.dn, createCA or createSubCA)
		csr.setKeyOptions(args.keyalgo, args.keysize, useSmartcard)
		if not createCA and not createSubCA and args.keyusage:
			for ku in args.keyusage:
				csr.setKeyUsage(ku)
		if not createCA and not createSubCA and args.extkeyusage:
			for ku in args.extkeyusage:
				csr.setExtendedKeyUsage(ku)
		if sanOpt:
			for s,v in sanOpt:
				csr.addSubjectAltName(s,v)

		if args.certpolicies:
			for oid in args.certpolicies:
				csr.addCertificatePolicy(oid, args.certpolicies[oid])

		if osslExtOpt:
			for OSSLextension in osslExtOpt:
				csr.addOSSLextension(OSSLextension)

		certificate = None
		if selfsigned:
			certificate = csr.selfSign(args.validity[0], args.validity[1],
							 			args.signalgo);
		else:
			issuer = DBHelper.getInstance().getCertificateFromDN(args.issuerdn)
			if not issuer:
				raise Exception(_("CLI_DN_CERT_NOT_FOUND_ERROR") % args.issuerdn)
			if not issuer.isCA():
				raise Exception(_("CLI_DN_CERT_NOT_A_CA_ERROR") % args.issuerdn)
			certificate = issuer.signCSR(csr,
							args.validity[0], args.validity[1],
				 			args.signalgo)
		if args.name != None:
			DBHelper.getInstance().changeCertificateInternalName(certificate, args.name)

		if not certificate:
			raise Exception(_("CLI_CERT_CREATION_ERROR"))

