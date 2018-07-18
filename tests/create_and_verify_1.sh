#!/bin/sh
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

set -e
. ./common.sh
test_init

$CLI_EXECUTABLE createca --dn "${TEST_HTTPS_ROOT}"  --signalgo SHA512RSA --keyalgo RSA --keysize 2048  --validity 10/10/2012-10/10/2014
$CLI_EXECUTABLE exportcert --dn "${TEST_HTTPS_ROOT}"

x509=`openssl x509 -in CA_DEVEL_HTTPS_ROOT_cert.pem  -noout -text`
#check version
test_or_print_error 'echo $x509 |grep -q "Version: 3 (0x2)"'\
	"Invalid Version"
#check subject
test_or_print_error 'echo $x509 |grep -q "Subject: C=FR, ST=France, L=Paris, O=FOO_O, OU=FOO_OU, CN=FOO_CN_ROOT"' \
	"Invalid Subject"
#check issuer
test_or_print_error 'echo $x509 |grep -q "Issuer: C=FR, ST=France, L=Paris, O=FOO_O, OU=FOO_OU, CN=FOO_CN_ROOT"' \
	"Invalid Issuer"
#check sign algo
test_or_print_error 'echo $x509 |grep -q "Signature Algorithm: sha512WithRSAEncryption"' \
	"Invalid Signature algo"
#check validity
test_or_print_error 'echo $x509 |grep -q "Validity Not Before: Oct 10 00:00:00 2012 GMT Not After : Oct 10 00:00:00 2014 GMT"' \
	"Invalid Validity"
#check public key algo
test_or_print_error 'echo $x509 |grep -q "Public Key Algorithm: rsaEncryption"' \
	"Invalid Public key algo"
#check public key size
test_or_print_error 'echo $x509 |grep -q "Public-Key: (2048 bit)"' \
	"Invalid public key size"
#check CA critical true
test_or_print_error 'echo $x509 |grep -q "X509v3 Basic Constraints: critical CA:TRUE"' \
	"Invalid EXT Basic Constraints"
#check CA key usage
test_or_print_error 'echo $x509 |grep -q "X509v3 Key Usage: critical Certificate Sign, CRL Sign"' \
	"Invalid EXT Key Usage"
