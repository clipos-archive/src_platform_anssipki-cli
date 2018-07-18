# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import sys
import argparse
from os import listdir
from os.path import isfile,join
from libanssipki import anssipki
from libanssipki.Conf import Conf
from libanssipki.DBHelper import DBHelper
from libanssipki.Template import parseTemplate
from CLIAction import CLIAction, UniqueAppendAction, parseDN, parseName
from libanssipkicli import _

class CLIInfo(CLIAction):
	actions = ["info"]

	def __init__(self, action = None):
		super(CLIInfo, self).__init__(action)

	@staticmethod
	def usage():
		print "\t" + "info: " + _("CLI_INFO_USAGE")

	def do(self, args):
		args = self.parser.parse_args(args)

		# list sign algo
		print _("CLI_AVAILABLE_SIGNALGO")
		for sa in anssipki.P11Helper.getInstance().listAvailableSignAlgorithms():
			print "\t", sa
		# list templates
		print _("CLI_AVAILABLE_TEMPLATES")
		for tmpDir in Conf.getValue('TEMPLATES_DIR'):
			for tmp in [ f for f in listdir(tmpDir)
				if (isfile(join(tmpDir, f)) and
					f.endswith(".tpl"))]:
				print "\t", tmp[:-4]
				template = parseTemplate(tmp[:-4])['values']
				for i in template:
					print "\t ",i,"=",template[i]
		# list key algo
		# list key sizes
		# list oids ?
