#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Riccardo Freixo

"""
Simple module to find AMI IDs based on attribute filters
"""

DOCUMENTATION = '''
---
module: ec2_find_ami
version_added: "1.8"
short_description: Find AutoScalingGroups based on ec2 tags.
description:
    - Finds and retrieves properties about AutoScalingGroups based on tags.
author: Riccardo Freixo
options:
  region:
    description:
      - The AWS region to use. If not specified then the value of the EC2_REGION environment variable, if any, is used.
    required: false
    aliases: ['aws_region', 'ec2_region']
  tags:
    description:
      - dictonary of key value tags to search for.
    required: true
    default: null
    aliases: []

extends_documentation_fragment: aws
'''

import sys

try:
    import boto
    import boto.ec2
except ImportError:
    print "failed=True msg='boto required for this module'"
    sys.exit(1)

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *


def find(module, connection, filters, **kwargs):
    # filters = {'tag:gitShortHash': '8ef351a'}
    try:
        amis = connection.get_all_images(
                filters=filters,
                executable_by=kwargs['executable_by'],
                owners=kwargs['owners']
                )
    except boto.exception.EC2ResponseError, error:
        module.fail_json(msg=str(error))

    ami_ids = {'ami_ids': [amis[i].id for i in range(0, len(amis), 1)]}
    return ami_ids

def main():
    """Main function"""
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            executable_by=dict(type='list'),
            owners=dict(type='list'),
            filters=dict(type='dict', required=True)
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    try:
        connection = ec2_connect(module)
        if not connection:
            module.fail_json(msg="failed to connect to AWS for the given region: %s" % str(region))
    except boto.exception.NoAuthHandlerFound, error:
        module.fail_json(msg=str(error))

    executable_by = module.params.get('executable_by')
    owners = module.params.get('owners')
    filters = module.params.get('filters')
    module.exit_json(
            changed=False,
            **find(
                module,
                connection,
                filters=filters,
                executable_by=executable_by,
                owners=owners
                )
            )

if __name__ == "__main__":
    main()
