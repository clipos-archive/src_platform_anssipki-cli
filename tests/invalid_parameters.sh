#!/bin/bash
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

# set -x
. ./common.sh
test_init

touch invalid_parameter_errors.txt

function testInvalid() {
	line=$1
	shift 1
	$*
	if [ $? -ne 1 ]; then
		echo "Test line $line failed"
		exit 1
	fi
}
alias testMe="testInvalid \$LINENO"

## Creating certificates ##
# Missing arguments
# dn
testMe anssipki_cli createca --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014  2> invalid_parameter_errors.txt
# signalgo
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
# keyalgo
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keysize 1024  --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
# keysize
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
# validity
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024 2>> invalid_parameter_errors.txt
# issuer
testMe anssipki_cli createcert --dn "${TEST_HTTPS_OTHER}" --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014 --keyusage KeyEncipherment:DigitalSignature 2>> invalid_parameter_errors.txt
testMe anssipki_cli createsubca --dn "${TEST_HTTPS_SERVER}" --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
# keyusage
testMe anssipki_cli createcert --dn "${TEST_HTTPS_OTHER}" --issuerDN "${TEST_HTTPS_SERVER}" --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014  2>> invalid_parameter_errors.txt

# Validity bad month
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/13/2012-10/10/2014 2>> invalid_parameter_errors.txt
# Validity bad day
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 42/12/2012-10/10/2014 2>> invalid_parameter_errors.txt
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 2>> invalid_parameter_errors.txt
# Validity notBefore > notAfter
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2015-10/10/2014 2>> invalid_parameter_errors.txt
# Validity notBefore == notAfter
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2014-10/10/2014 2>> invalid_parameter_errors.txt
#testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2014+0d 2>> invalid_parameter_errors.txt
#testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity +0d 2>> invalid_parameter_errors.txt
# bad key size
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1025  --validity 29/02/2013-10/10/2014 2>> invalid_parameter_errors.txt
# bad key type
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSAA --keysize 1025  --validity 29/02/2013-10/10/2014 2>> invalid_parameter_errors.txt
# bad sign algo
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSAA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 2>> invalid_parameter_errors.txt
# bad DN
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT},AA=1"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 2>> invalid_parameter_errors.txt
testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT},CN=FOO"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 2>> invalid_parameter_errors.txt
# bad KeyUsage
testMe anssipki_cli createcert --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 --keyusage KeyEncipherment:AA 2>> invalid_parameter_errors.txt
# bad KeyUsage for a (sub)CA
#testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024 --keyusage DigitalSignature --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
#testMe anssipki_cli createsubca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024 --keyusage DigitalSignature --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
# bad ExtendedKeyUsage
testMe anssipki_cli createcert --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 --extkeyusage ServerAuth:AA 2>> invalid_parameter_errors.txt
# bad ExtendedKeyUsage for a (sub)CA
#testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024 --extkeyusage ServerAuth --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
#testMe anssipki_cli createsubca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024 --extkeyusage ServerAuth --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt

# existing DN
#testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/12/2012-10/10/2014 2>> invalid_parameter_errors.txt
#testMe anssipki_cli createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/12/2012-10/10/2014 2>> invalid_parameter_errors.txt


## Exporting certificates ##
# Missing arguments
testMe anssipki_cli exportcert 2>> invalid_parameter_errors.txt
testMe anssipki_cli exportp12 2>> invalid_parameter_errors.txt
# Certificate not exists
testMe anssipki_cli exportcert --dn CN=nobody 2>> invalid_parameter_errors.txt
testMe anssipki_cli exportp12 --dn CN=nobody 2>> invalid_parameter_errors.txt
# File already exists
anssipki_cli createca --dn "${TEST_HTTPS_ROOT}" --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014 2>> invalid_parameter_errors.txt
anssipki_cli exportcert --dn "${TEST_HTTPS_ROOT}" --filename root.pem 2>> invalid_parameter_errors.txt
testMe anssipki_cli exportcert --dn "${TEST_HTTPS_ROOT}" --filename root.pem 2>> invalid_parameter_errors.txt

anssipki_cli createcert --dn "${TEST_HTTPS_OTHER}"  --issuerDN "${TEST_HTTPS_ROOT}" --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 29/02/2013-10/10/2014 --keyusage KeyEncipherment 2>> invalid_parameter_errors.txt
anssipki_cli exportp12 --dn "${TEST_HTTPS_OTHER}" --filename other.p12 --password foo 2>> invalid_parameter_errors.txt
testMe anssipki_cli exportp12 --dn "${TEST_HTTPS_OTHER}" --filename other.p12 --password foo 2>> invalid_parameter_errors.txt

rm -f root.pem other.p12

## Showing certificates ##
# Missing arguments
testMe anssipki_cli show 2>> invalid_parameter_errors.txt
testMe anssipki_cli show --dn 2>> invalid_parameter_errors.txt
# Bad argument
testMe anssipki_cli show --dna 2>> invalid_parameter_errors.txt
# Bad CA
testMe anssipki_cli listcerts --issuerDN CN=foo 2>> invalid_parameter_errors.txt

rm -f libanssipki_client.db
