#!/bin/sh
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

set -e
. ./common.sh
test_init

$CLI_EXECUTABLE createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014
$CLI_EXECUTABLE createsubca --issuerdn "${TEST_HTTPS_ROOT}" --dn "${TEST_HTTPS_SERVER}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014
$CLI_EXECUTABLE createcert --issuerdn "${TEST_HTTPS_SERVER}" --dn "${TEST_HTTPS_OTHER}"  --signalgo SHA512RSA --keyalgo RSA --keysize 1024  --validity 10/10/2012-10/10/2014 --keyusage KeyEncipherment:DigitalSignature
$CLI_EXECUTABLE exportcert  --dn "${TEST_HTTPS_OTHER}" --chain
test_or_print_error 'openssl verify  -CAfile js-test_cert.pem  js-test_cert.pem  > /dev/null' \
	"Certificate chain verification failed"

$CLI_EXECUTABLE list >"${NAME}.txt.1"
test_or_print_error 'diff -q "../${NAME}.txt.1" "${NAME}.txt.1"'\
	"List command output is different"
rm "${NAME}.txt.1"
