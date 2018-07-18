# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import sys
import argparse
import subprocess
from libanssipki.DBHelper import DBHelper
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName, parserError
from libanssipkicli import _
from libanssipki import anssipki
from libanssipkicli import _



class CLIAttachCA(CLIAction):
	actions = ["attachca"]

	def __init__(self, action):
		super(CLIAttachCA, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--in",
								help=_("CLI_IMPORT_IN_OPTION_HELP"))


	@staticmethod
	def usage():
		print "\t" + ', '.join(CLIAttachCA.actions) + " : %s" % _("CLI_ATTACHCA_USAGE")

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
		if not cert.isCA():
			raise Exception(_("CLI_DN_CERT_NOT_A_CA_ERROR") % cert.getName())

		if not cert.isSelfSigned():
			raise Exception(_("CLI_DN_CERT_NOT_SELFSIGNED_ERROR") % cert.getName())

		if vars(args)['in'] == None:
			raise Exception(_("CLI_IMPORT_NO_IN_ERROR"))

		with open(vars(args)['in'], "r") as fp:
			der = fp.read()

		if not cert.attachCA(der):
			raise Exception(_("CLI_ATTACH_ERROR"))



