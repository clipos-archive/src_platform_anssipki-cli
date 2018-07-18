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


class CLIShowLogs(CLIAction):
	actions = ["showlogs"]

	def __init__(self, action):
		super(CLIShowLogs, self).__init__(action)
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))


	@staticmethod
	def usage():
		print "\t" + ', '.join(CLIShowLogs.actions) + ": " + _("CLI_SHOWLOGS_USAGE")

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

		if cert:
			logs = DBHelper.getInstance().getCertLogActions(cert.getDbCertID())
		else:
			logs = DBHelper.getInstance().getLogActions()

		for l in logs:
			print l
