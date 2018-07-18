# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

import os
import sys
import argparse
import re
from datetime import datetime, timedelta, date
import calendar

DNRe = "((?:O|OU|C|CN|S|ST|L)=[^,]+)*(?:O|OU|C|CN|S|ST|L)=[^,]+"
NameRe = "[^,]+"

def parseDN(string):
	if not re.match(DNRe, string): raise Exception("Invalid DN format")
	return string

def parseName(string):
	if not re.match(NameRe, string): raise Exception("Invalid Name format")
	return string

def addMonths(current, months):
	month = current.month - 1 + months
	year = current.year + month / 12
	month = month % 12 + 1
	day = min(current.day, calendar.monthrange(year,month)[1])
	return date(year, month, day)

def parseValidity(string):
	datefrom = dateto = None
	matches1 = re.match("^([0-9]+/[0-9]+/[0-9]+)-([0-9]+/[0-9]+/[0-9]+)$", string)
	matches2 = re.match("^([0-9]+/[0-9]+/[0-9]+)\+([0-9]+d)?([0-9]+m)?([0-9]+y)$", string)
	matches3 = re.match("^\+([0-9]+d)?([0-9]+m)?([0-9]+y)?$", string)
	if matches1:
		datefrom = (datetime.strptime(matches1.group(1), "%d/%m/%Y")).date()
		dateto = (datetime.strptime(matches1.group(2), "%d/%m/%Y")).date()
	elif matches2:
		datefrom = dateto = datetime.strptime(matches2.group(1), "%d/%m/%Y").date()
		if matches2.group(2):
			dateto += timedelta(int(matches2.group(2)[:-1]))
		if matches2.group(3):
			dateto = addMonths(dateto, int(matches2.group(3)[:-1]))
		if matches2.group(4):
			dateto = addMonths(dateto, 12 * int(matches2.group(4)[:-1]))
	elif matches3:
		datefrom = dateto = date.today()
		if matches3.group(1):
			dateto += timedelta(int(matches3.group(1)[:-1]))
		if matches3.group(2):
			dateto = addMonths(dateto, int(matches3.group(2)[:-1]))
		if matches3.group(3):
			dateto = addMonths(dateto, 12 * int(matches3.group(3)[:-1]))
	if not datefrom or not dateto:
		raise Exception("Invalid validity")
	return (datefrom.strftime("%y%m%d000000Z"), dateto.strftime("%y%m%d000000Z"))

def parserError(message):
	raise Exception(message)

def createArgumentParser(action):
		parser = argparse.ArgumentParser(prog=action, formatter_class=argparse.RawTextHelpFormatter)
		parser.error = parserError
		return parser

class CLIAction(object):
	parser = None

	def __init__(self, action):
		self.action = action
		self.parser = createArgumentParser(action)

	@staticmethod
	def usage():
		raise Exception("Internal Error : CLIAction::usage should be overloaded")

class UniqueAppendAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		if getattr(namespace, self.dest) != None: raise Exception ("%s is already set" % self.dest)
		setattr(namespace, self.dest, values)
