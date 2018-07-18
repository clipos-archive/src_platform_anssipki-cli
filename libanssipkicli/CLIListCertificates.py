# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import sys
import argparse
from libanssipki import anssipki
from libanssipki.DBHelper import DBHelper
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName
from libanssipkicli import _

class CLIListCertificates(CLIAction):
	actions = ["list"]

	def __init__(self, action = None):
		super(CLIListCertificates, self).__init__(action)
		self.parser.add_argument("--dn", type=parseDN, action=UniqueAppendAction,
								help=_("CLI_DN_OPTION_HELP"))
		self.parser.add_argument("--name", type=parseName, action=UniqueAppendAction,
								help=_("CLI_NAME_OPTION_HELP"))
		self.parser.add_argument("--verbose", default=False, action='store_true',
								help="")
		self.parser.add_argument("--selfsigned", default=False, action='store_true',
								help="")

	@staticmethod
	def usage():
		print "\t" + ', '.join(CLIListCertificates.actions) + ": " + _("CLI_LIST_USAGE")

	def printSelfSigned(self, verbose):
		selfSignedCerts = DBHelper.getInstance().getSelfSignedCertificateList()
		if len(selfSignedCerts) > 0:
			print "Certificats auto-signés :"
			for c in selfSignedCerts :
				print "%s%s" % ("\t", c.getName())

	def printTreeCA(self, cert, depth=0, verbose=False):
		print "%s%s%s (%s)%s" % ("==> "*depth,
			"*" if cert.isCA() else " ",
			cert.getCacheDN(),
			cert.getName(),
			" (SC)" if cert.hasKeyGeneratedOnSmartCard() else "")
		if verbose:
			print " %sSubject:%s" % ("    "*depth, cert.getCacheDN())
		if cert.isCA():
			for children in DBHelper.getInstance().getChildren(cert):
				self.printTreeCA(children, depth + 1, verbose)

	def do(self, args):
		args = self.parser.parse_args(args)

		if args.selfsigned:
			self.printSelfSigned(args.verbose)
			return

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
			self.printTreeCA(cert, 0, args.verbose)
		else:
			rootCAList = DBHelper.getInstance().getRootCAList()
			if len(rootCAList) == 0:
				print _("CLI_LIST_NO_AC_FOUND")
			else:
				for r in rootCAList:
					self.printTreeCA(r, 0, args.verbose)
