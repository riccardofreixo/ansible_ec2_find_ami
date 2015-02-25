#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest

try:
    import boto
    import boto.ec2
except ImportError:
    print "failed=True msg='boto required for this test suite'"
    sys.exit(1)

try:
    from moto import mock_ec2
except ImportError:
    print "failed=True msg='moto required for this test suite'"
    sys.exit(1)

# from ansible.module_utils.basic import *
# from ansible.module_utils.ec2 import *


class TestEc2FindAmi(unittest.TestCase):

    def setUp(self):
        pass

    @mock_ec2
    def test_match_one_as_group(self):
        pass

if __name__ == '__main__':
    unittest.main()
