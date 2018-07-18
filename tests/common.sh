# -*- sh -*-
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

NAME="$(basename -- "${0%.*}")"
export CLI_EXECUTABLE="anssipkicli"
export CONFFILE=`pwd`/tmp/anssipki.ini

export WITH_PROXY=1

test_init_env() {
	if [ -z "${PKCS11_MODULE}" ]; then
		if [ -f "/usr/lib/softhsm/libsofthsm.so" ]; then
			export PKCS11_MODULE="/usr/lib/softhsm/libsofthsm.so"
		else
			echo "Need to set the PKCS11_MODULE variable." >&2
			return 1
		fi
	fi
	export PKCS11_PIN="4242"
	export PKCS11_LABEL="test"
	export SOFTHSM2_CONF=`pwd`"/.softhsm2.conf"
	echo "directories.tokendir = "`pwd`"/.softhsm2_tokens" > ${SOFTHSM2_CONF}
	rm -rf `pwd`"/.softhsm2_tokens"
	mkdir `pwd`"/.softhsm2_tokens"
	export SOFTHSM2_ANSSIPKI_STATE_FILE="/tmp/alea"
	echo "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" > ${SOFTHSM2_ANSSIPKI_STATE_FILE}

}

test_init() {
	test_init_env

	rm -rf
	softhsm2-util --init-token --slot 0 --label "${PKCS11_LABEL}" --pin "${PKCS11_PIN}" --so-pin "${PKCS11_PIN}"

	rm -rf tmp
	if [ ! -d tmp ]; then
		mkdir tmp
	fi

	cp anssipki.ini tmp/
	echo "PKCS11_HOST_MODULE=${PKCS11_MODULE}" >> tmp/anssipki.ini
	echo "PKCS11_HOST_LABEL=${PKCS11_LABEL}" >> tmp/anssipki.ini
	echo "PKCS11_HOST_PIN=${PKCS11_PIN}" >> tmp/anssipki.ini
	echo "USE_P11PROX=${WITH_PROXY}" >> tmp/anssipki.ini



	cd tmp

	if [ -f test.db ]; then
		rm -f test.db
	fi
}

test_or_print_error() {
	eval $1  >/dev/null 2> /dev/null ||(echo $2 1>&2 && false)
}

TEST_HTTPS_ROOT="C=FR,ST=France,L=Paris,O=FOO_O,OU=FOO_OU,CN=FOO_CN_ROOT"
TEST_HTTPS_SERVER="C=FR,ST=France,L=Paris,O=FOO_O,OU=FOO_OU,CN=FOO_CN_SERVER"
TEST_HTTPS_OTHER="C=FR,ST=France,L=Paris,O=BAR_O,OU=BAR_OU,CN=BAR_CN"
