#!/bin/sh
# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright © 2013-2018 ANSSI. All Rights Reserved.

echo "create_and_verify_1.sh"
bash create_and_verify_1.sh

echo "create_and_verify_2.sh"
bash create_and_verify_2.sh

echo "create_and_verify_3.sh"
bash create_and_verify_3.sh

echo "create_and_renew_1.sh"
bash create_and_renew_1.sh

echo "create_and_export_1.sh"
bash create_and_export_1.sh
