#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

from distutils.core import setup, Extension
from distutils.cmd import Command
from distutils.errors import CompileError
from distutils.command.build import build as _build
from glob import glob
import subprocess
import os.path

class build_trans(Command):
	""" Compile .po files into .mo files """
	def initialize_options(self):
		pass
	def finalize_options(self):
		pass
	def run(self):
		for pofile in glob('locales/*/*/*.po'):
			mofile = pofile[:-2]+"mo"
			if (not os.path.exists(mofile) or
				os.path.getmtime(pofile) > os.path.getmtime(mofile)):
				print 'Compiling %s' % pofile
				if subprocess.call(["msgfmt", "-o", mofile, pofile]) != 0:
					raise CompileError ("Locales compilation failed")

class build(_build):
	sub_commands = _build.sub_commands + [('build_trans', None)]
	def run(self):
		_build.run(self)

cmdclass = {
	'build': build,
	'build_trans': build_trans
}

setup(name='anssipki-cli',
	version="1.3.0",
	description="",
	author="Baptiste Gourdin",
	author_email="clipos@ssi.gouv.fr",
	cmdclass = cmdclass,
	scripts=["anssipkicli"],
	packages=["libanssipkicli"],
	data_files=[
			('share/anssipki/locales/en_US/LC_MESSAGES', ['locales/en_US/LC_MESSAGES/anssipkicli.mo']),
			('share/anssipki/locales/fr_FR/LC_MESSAGES', ['locales/fr_FR/LC_MESSAGES/anssipkicli.mo']),
				],
	)
