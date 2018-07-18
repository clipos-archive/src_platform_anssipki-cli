# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import sys
import argparse
import subprocess
import getpass
from libanssipki.DBHelper import DBHelper
from libanssipki.Conf import Conf
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName, parserError
from libanssipkicli import _


class CLIExportCertificate(CLIAction):
	actions = ["exportcert", "exportp12", "exportcsr"]

	def __init__(self, action):
		super(CLIExportCertificate, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--out",
								help=_("CLI_EXPORT_OUT_OPTION_HELP"))
		if action == "exportp12" or action == "exportcert":
			self.parser.add_argument("--chain", default=False, action='store_true',
									help=_("CLI_EXPORT_CHAIN_OPTION_HELP"))
		if action == "exportp12":
			self.parser.add_argument("--password", action=UniqueAppendAction,
									help=_("CLI_EXPORT_PASSWORD_OPTION_HELP"))
			self.parser.add_argument("--randpass", default=False, action='store_true',
						 help=_("CLI_EXPORT_RANDPASS_OPTION_HELP"))


	@staticmethod
	def usage():
		print "\t" + "exportcert: %s" % _("CLI_EXPORTCERT_USAGE")
		print "\t" + "exportp12 : %s" % _("CLI_EXPORTP12_USAGE")
		print "\t" + "exportcsr : %s" % _("CLI_EXPORTCSR_USAGE")


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

		if self.action == "exportcsr":
			csr = cert.toCSR()
			if args.out != None:
				outputFile = args.out
			else:
				outputFile = "./%s.csr" % cert.getName()
			with open(outputFile, "w") as f:
				f.write(csr)

		if self.action == "exportcert":
			certchain = []
			certchain.append(cert)
			if args.out != None:
				outputFile = args.out
			else:
				outputFile = "./%s_cert.pem" % cert.getName()

			if args.chain and not cert.isSelfSigned():
				rootFound = False
				while not rootFound:
					issuer = cert.getIssuerCa()
					certchain.append(issuer)
					if issuer.isSelfSigned():
						rootFound = True
					cert = issuer

			out = ""
			for cert in certchain:
				#FIXME devrait être fait directement avec la libopenssl plutot que via un appel
				p = subprocess.Popen(["openssl","x509","-inform","der", "-outform", "pem"],
					stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				stdout, stderr = p.communicate(cert.getX509CertDER())
				out += stdout

			with open(outputFile, "w") as f:
				f.write(out)

		if self.action == "exportp12":
			password = None
			if Conf.getValue("USE_P11PROX"):
				password = "proxy" # the real password will be provided by a safe prompt
			elif args.password:
				password = args.password
			elif args.randpass:
				f = open("/dev/urandom", "rb")
				password = ''
				while len(password) < 16:
					b = f.read(1)
					if b.isalnum():
						password += b
				f.close()
				print "%s: %s" % (_("CLI_PASSWORD"), password)
			else:
				p1 = None
				p2 = None
				try:
					while (p1 == None) or (p1 != p2):
						p1 = getpass.getpass("%s:" % _("CLI_PASSWORD"))
						p2 = getpass.getpass("%s (bis):" % _("CLI_PASSWORD"))
						if p1 != p2:
							print _("CLI_PASSWORD_MISSMATCH")
					password = p1
				except KeyboardInterrupt:
					return
			p12 = cert.extractToP12(password, args.chain)
			if args.out != None:
				outputFile = args.out
			else:
				outputFile = "./%s.p12" % cert.getName()
			with open(outputFile, "w") as f:
				f.write(p12)
