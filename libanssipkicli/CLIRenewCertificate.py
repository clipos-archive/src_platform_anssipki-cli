# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import sys
import os
import argparse
import subprocess
from libanssipki.DBHelper import DBHelper
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName, parseValidity
from libanssipkicli import _

class CLIRenewCertificate(CLIAction):
	actions = ["renew"]

	def __init__(self, action):
		super(CLIRenewCertificate, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--validity", type=parseValidity, action=UniqueAppendAction,
								help=_("CLI_VALIDITY_OPTION_HELP"))

	@staticmethod
	def usage():
		print "\t" + ', '.join(CLIRenewCertificate.actions) + ": " +  _("CLI_RENEW_USAGE")

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

		if cert.isSelfSigned():
			if not cert.isCA():
				raise Exception(_("CLI_RENEW_SELFSIGN_NOT_IMPLEMENTED"))
			cert = cert.renew(cert)
		else:
			cert = cert.getIssuerCa().renewCertificate(cert, args.validity[0], args.validity[1])
