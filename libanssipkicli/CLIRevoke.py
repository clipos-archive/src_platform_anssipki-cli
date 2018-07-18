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
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName, parseValidity
from libanssipkicli import _


class CLIRevoke(CLIAction):
	actions = ["revoke"]

	def __init__(self, action):
		super(CLIRevoke, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--reason", type=str, action=UniqueAppendAction,
								help=_("CLI_REVOKE_REASON_OPTION_HELP")),

	@staticmethod
	def usage():
		print "\t" + ', '.join(CLIRevoke.actions) + ": " +  _("CLI_REVOKE_USAGE")


	def do(self, args):
		args = self.parser.parse_args(args)

		cert = None
		if args.dn != None:
			cert = DBHelper.getInstance().getCertificateFromDN(args.dn)
			if not cert:
				raise Exception(_("CLI_DN_CERT_NOT_FOUND_ERROR") % args.dn)
		if args.name != None:
			if cert:
				raise Exception(_("CLI_DN_AND_NAME_SET_ERROR"))
			cert = DBHelper.getInstance().getCertificateFromName(args.name)
			if not cert:
				raise Exception(_("CLI_NAME_CERT_NOT_FOUND_ERROR") % args.name)

		if not cert:
			raise Exception(_("CLI_NO_DN_NAME_SET_ERROR"))

		cert.revoke(args.reason)



class CLICreateCRL(CLIAction):
	actions = ["createcrl"]

	def __init__(self, action):
		super(CLICreateCRL, self).__init__(action)
		self.parser.add_argument("--issuername", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--issuerdn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--out",
								help=_("CLI_CREATECRL_OUT_OPTION_HELP"))

	@staticmethod
	def usage():
		print "\t" + ', '.join(CLICreateCRL.actions) + ": " + _("CLI_CREATECRL_USAGE")


	def do(self, args):
		args = self.parser.parse_args(args)

		cert = None
		if args.issuerdn != None:
			cert = DBHelper.getInstance().getCertificateFromDN(args.issuerdn)
			if not cert:
				raise Exception(_("CLI_DN_CERT_NOT_FOUND_ERROR") % args.issuerdn)
		if args.issuername != None:
			if cert:
				raise Exception(_("CLI_DN_AND_NAME_SET_ERROR"))
			cert = DBHelper.getInstance().getCertificateFromName(args.issuername)
			if not cert:
				raise Exception(_("CLI_NAME_CERT_NOT_FOUND_ERROR") % args.issuername)

		if not cert:
			raise Exception(_("CLI_NO_DN_NAME_SET_ERROR"))

		if not cert.isCA():
			raise Exception(_("CLI_DN_CERT_NOT_A_CA_ERROR") % args.issuerdn)

		crl = cert.buildCRL()

		if args.out != None:
			outputFile = args.out
		else:
			outputFile = "./%s.crl" % cert.getName()
		with open(outputFile, "w") as f:
			f.write(crl)

		print _("CLI_CRL_WRITTEN_TO") % outputFile
