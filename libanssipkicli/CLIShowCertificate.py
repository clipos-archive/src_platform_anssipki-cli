# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import os
import sys
import argparse
import subprocess
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName
from libanssipki.DBHelper import DBHelper
from libanssipkicli import _


class CLIShowCertificate(CLIAction):
	actions = ["showcert"]

	def __init__(self, action = None):
		super(CLIShowCertificate, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))


	@staticmethod
	def usage():
		print "\t" + ', '.join(CLIShowCertificate.actions) + " : Display certificate information"

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

		der = cert.getX509CertDER();

		tmpfile = "./%s_cert.der.tmp" % cert.getCacheDN()
		f = open(tmpfile, "w")
		f.write(der)
		f.close()

		#FIXME devrait être fait directement avec la libopenssl plutot que via un appel
		out = subprocess.check_output("openssl x509 -inform der -text -noout -in %s" % tmpfile,
										shell=True)
		sys.stdout.write(out)
		os.remove(tmpfile)
