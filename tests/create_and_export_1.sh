#!/bin/sh
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

set -e
. ./common.sh
test_init

cat > scenario.txt <<EOF
createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014
createsubca --issuerdn "${TEST_HTTPS_ROOT}" --dn "${TEST_HTTPS_SERVER}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014
createcert --issuerdn "${TEST_HTTPS_SERVER}" --dn "${TEST_HTTPS_OTHER}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014 --keyusage KeyEncipherment:DigitalSignature
exportp12 --dn "${TEST_HTTPS_OTHER}" --password toto --chain
EOF

$CLI_EXECUTABLE -s scenario.txt

test_or_print_error 'openssl pkcs12 -in js-test.p12 -nodes -passin pass:toto' \
	"P12 import failed"

true
