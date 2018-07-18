#!/bin/sh
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

set -e
. ./common.sh
test_init

PWD=`pwd`
cat > myca.tpl <<EOF
[CERTIFICATE]
signalgo=SHA512RSA
keyalgo=RSA
keysize=1024
validity=+20y
EOF

cat > mycert.tpl <<EOF
[CERTIFICATE]
signalgo=SHA512RSA
keyalgo=RSA
keysize=1024
validity=+3y
EOF

cat > myssl.tpl <<EOF
[PARENT]
template=${PWD}/mycert.tpl

[CERTIFICATE]
keyusage=DigitalSignature:KeyEncipherment
extkeyusage=ServerAuth
EOF

$CLI_EXECUTABLE createca --template "myca.tpl" --dn "${TEST_HTTPS_ROOT}"
$CLI_EXECUTABLE createsubca --template "myca.tpl" --issuerdn "${TEST_HTTPS_ROOT}" --dn "${TEST_HTTPS_SERVER}"
$CLI_EXECUTABLE createcert  --template "myssl.tpl" --issuerdn "${TEST_HTTPS_SERVER}" --dn "${TEST_HTTPS_OTHER}"
$CLI_EXECUTABLE exportcert  --dn "${TEST_HTTPS_ROOT}"
$CLI_EXECUTABLE exportcert  --dn "${TEST_HTTPS_SERVER}"
$CLI_EXECUTABLE exportcert  --dn "${TEST_HTTPS_OTHER}"

$CLI_EXECUTABLE list >"${NAME}.txt.1"
diff -q "../${NAME}.txt.1" "${NAME}.txt.1"
rm "${NAME}.txt.1"

openssl verify  -CAfile CA_DEVEL_HTTPS_ROOT_cert.pem  CA_DEVEL_HTTPS_SERVERS_cert.pem   > /dev/null
cat CA_DEVEL_HTTPS_ROOT_cert.pem  CA_DEVEL_HTTPS_SERVERS_cert.pem  > CA_DEVEL_HTTPS_ROOT_SERVERS_cert.pem
openssl verify  -CAfile CA_DEVEL_HTTPS_ROOT_SERVERS_cert.pem  js-test_cert.pem  > /dev/null
showout=`$CLI_EXECUTABLE show --dn "${TEST_HTTPS_OTHER}"`

openssl verify  -CAfile CA_DEVEL_HTTPS_ROOT_cert.pem  CA_DEVEL_HTTPS_SERVERS_cert.pem  > /dev/null
cat CA_DEVEL_HTTPS_ROOT_cert.pem  CA_DEVEL_HTTPS_SERVERS_cert.pem  > CA_DEVEL_HTTPS_ROOT_SERVERS_cert.pem

openssl verify  -CAfile CA_DEVEL_HTTPS_ROOT_SERVERS_cert.pem  js-test_cert.pem  > /dev/null

$CLI_EXECUTABLE show --dn "${TEST_HTTPS_OTHER}" >"${NAME}.txt.2"
openssl x509 -noout -text -in js-test_cert.pem >"${NAME}.txt.3"
diff -q "${NAME}.txt.2" "${NAME}.txt.3"
