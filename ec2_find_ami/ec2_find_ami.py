#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Riccardo Freixo

"""
Simple Ansible module to find AMI IDs based on attribute filters
"""

DOCUMENTATION = '''
---
module: ec2_find_ami
version_added: "1.8"
short_description: Find AMIs based on attributes.
description:
    - Finds and retrieves properties about AMIs based on AMI attributes.
author: Riccardo Freixo
options:
  region:
    description:
      - The AWS region to use. If not specified then the value of the EC2_REGION environment variable, if any, is used.
    required: false
    aliases: ['aws_region', 'ec2_region']
  owners:
    description:
      - Filter the images by the owner. Specify an AWS account ID, amazon (owner is Amazon), aws-marketplace (owner is AWS Marketplace), self (owner is the sender of the request).
    required: false
    default: self
    aliases: []
  executable_by:
    description:
      - Filter by users with explicit launch permissions. Specify an AWS account ID, self (the sender of the request), or all (public AMIs).
    required: false
    default: []
    aliases: []
  name:
    description:
      - Filter by the image name.
    required: false
    default: []
    aliases: []
  tags:
    description:
      - Filter by tags. This filter differs from the tag_key and tag_value filters in that it matches both the key and values provided. This filter is independent of the tag_key and tag_value filters.
    required: false
    default: []
    aliases: []
  tag_key:
    description:
      - Filter by the key of a tag assigned to the resource. This filter is independent of the tag-value filter. For example, if you use both the filter "tag_key=Purpose" and the filter "tag_value=X", you get any resources assigned both the tag key Purpose (regardless of what the tag's value is), and the tag value X (regardless of what the tag's key is). If you want to list only resources where Purpose is X, see the tags filter.
    required: false
    default: []
    aliases: []
  tag_value:
    description:
      - Filter by the value of a tag assigned to the resource. This filter is independent of the tag_key filter.
    required: false
    default: []
    aliases: []
  state:
    description:
      - Filter by the state of the image.
    required: false
    choices: ['available', 'pending', 'failed']
    default: []
    aliases: []
  architecture:
    description:
      - Filter by the image architecture.
    required: false
    choices: ['i386', 'x86_64']
    default: []
    aliases: []
  decription:
    description:
      - Filter by the description of the image.
    required: false
    default: []
    aliases: []
  hypervisor:
    description:
      - Filter by the hypervisor type.
    required: false
    choices: ['ovm', 'xen']
    default: []
    aliases: []
  image_id:
    description:
      - Filter by the image ID.
    required: false
    default: []
    aliases: []
  image_type:
    description:
      - Filter by the image type.
    required: false
    choices: ['machine', 'kernel', 'ramdisk']
    default: []
    aliases: []
  is_public:
    description:
      - Filter by whether the machine is public.
    required: false
    default: []
    aliases: []
  kernel_id:
    description:
      - Filter by the Kernel ID.
    required: false
    default: []
    aliases: []
  manifest_location:
    description:
      - Filter by location of the image manifest.
    required: false
    default: []
    aliases: []
  owner_alias:
    description:
      - Filter by the AWS account alias (for example, amazon).
    required: false
    default: []
    aliases: []
  owner_id:
    description:
      - Filter by the AWS account ID of the image owner.
    required: false
    default: []
    aliases: []
  platform:
    description:
      - Filter by the platform. To only list Windows-based AMIs, use windows.
    required: false
    default: []
    aliases: []
  product_code:
    description:
      - Filter by the product code.
    required: false
    default: []
    aliases: []
  product_code_type:
    description:
      - Filter by the type of the product code.
    required: false
    choices: ['devpay', 'marketplace']
    default: []
    aliases: []
  ramdisk_id:
    description:
      - Filter by the RAM disk ID.
    required: false
    default: []
    aliases: []
  root_device_name:
    description:
      - Filter by the name of the root device volume (for example, /dev/sda1).
    required: false
    default: []
    aliases: []
  root_device_type:
    description:
      - Filter by the type of the root device volume.
    required: false
    choices: ['ebs', 'instance-store']
    default: []
    aliases: []
  root_device_type:
    description:
      - Filter by the type of the root device volume.
    required: false
    choices: ['ebs', 'instance-store']
    default: []
    aliases: []
  virtualization_type:
    description:
      - Filter by the virtualization type.
    required: false
    choices: ['paravirtual', 'hvm']
    default: []
    aliases: []

extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Find instances with tags foo: bar
- ec2_find_ami:
    region: eu-west-1
      tags:
        foo: bar

# Find amazon owned instances with virtualization_type: hvm
- ec2_find_ami:
    region: eu-west-1
    owners: amazon
    virtualization_type: hvm

# Find and register all self-owned AMIs with root device type instance-store
- ec2_find_ami:
    region: eu-west-1
    root_device_type: instance-store
  register: my_instance_store_amis

- debug: var=my_instance_store_amis
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

AMI_ATTRIBUTES = (
        'id', 'location', 'state', 'ownerId', 'owner_id', 'owner_alias',
        'is_public', 'architecture', 'platform', 'type', 'kernel_id',
        'ramdisk_id', 'name', 'description', 'product_codes',
        'billing_products', 'root_device_type', 'root_device_name',
        'virtualization_type', 'hypervisor', 'instance_lifecycle',
        'sriov_net_support'
        )

SEARCH_FILTERS = {
        'name': 'name',
        'tag_key': 'tag-key',
        'tag_value': 'tag-value',
        'state': 'state',
        'architecture': 'architecture',
        'description': 'description',
        'hypervisor': 'hypervisor',
        'image_id': 'image-id',
        'image_type': 'image-type',
        'is_public': 'is-public',
        'kernel_id': 'kernel-id',
        'manifest_location': 'manifest-location',
        'owner_alias': 'owner-alias',
        'owner_id': 'owner-id',
        'platform': 'platform',
        'product_code': 'product-code',
        'product_code_type': 'product-code.type',
        'ramdisk_id': 'ramdisk-id',
        'root_device_name': 'root-device-name',
        'root_device_type': 'root-device-type',
        'virtualization_type': 'virtualization-type'
        }


def parse_filters(module):
    """
    Returns a dictionary with filters compatible with boto.ec2.connection.get_all_images

    :type module: :class:`ansible.module_utils.basic.AnsibleModule`
    :param module: an Ansible module.

    :rtype: dict
    :return: a dict with filters compatible with boto.ec2.connection.get_all_images
    """
    filters = {v: module.params.get(k) for k, v in SEARCH_FILTERS.iteritems() if k in module.params}
    if 'tags' in module.params:
        filters.update({'tag:'+key: value for key, value in module.params.get('tags').iteritems()})
    return filters


def get_properties(module, ami):
    """
    Returns a dictionary with the properties of ami

    :type module: :class:`ansible.module_utils.basic.AnsibleModule`
    :param module: an Ansible module.

    :type ami: :class:`boto.ec2.image.Image`
    :param ami: an EC2 Image, a.k.a AMI

    :rtype: dict
    :return: a dict with the properties of ami
    """
    properties = dict((attr, getattr(ami, attr)) for attr in AMI_ATTRIBUTES)
    properties.update(block_device_mapping=[block_device for block_device in ami.block_device_mapping])
    return properties


def find(module, connection, **kwargs):
    """
    Returns a dict with a list of dicts, each containing the properties of AMIs matching the filtering heuristics

    :type module: :class:`ansible.module_utils.basic.AnsibleModule`
    :param module: an Ansible module.

    :type connection: :class:`boto.ec2.connection.EC2Connection`
    :param connection: a connection to ec2

    :rtype: dict
    :return: a dict with a list of dicts, each containing the properties of AMIs matching the filtering heuristics
    """
    filters = parse_filters(module)
    try:
        amis = connection.get_all_images(
                filters=filters,
                owners=kwargs['owners'],
                executable_by=kwargs['executable_by']
                )
    except boto.exception.EC2ResponseError, error:
        module.fail_json(msg=str(error))

    ami_list = {'amis': [get_properties(module, ami) for ami in amis]}
    return ami_list


def main():
    """Main function"""
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            owners=dict(type='list', default='self'),
            executable_by=dict(type='list'),
            name=dict(type='str'),
            tags=dict(type='dict'),
            tag_key=dict(type='list'),
            tag_value=dict(type='list'),
            state=dict(type='str', choices=['available', 'pending', 'failed']),
            architecture=dict(type='str', choices=['i386', 'x86_64']),
            description=dict(type='str'),
            hypervisor=dict(type='str', choices=['ovm', 'xen']),
            image_id=dict(type='str'),
            image_type=dict(type='str', choices=['machine', 'kernel', 'ramdisk']),
            is_public=dict(type='bool'),
            kernel_id=dict(type='str'),
            manifest_location=dict(type='str'),
            owner_alias=dict(type='str'),
            owner_id=dict(type='list'),
            platform=dict(type='str'),
            product_code=dict(type='str'),
            product_code_type=dict(type='str', choices=['devpay', 'marketplace']),
            ramdisk_id=dict(type='str'),
            root_device_name=dict(type='str'),
            root_device_type=dict(type='str', choices=['ebs', 'instance-store']),
            virtualization_type=dict(type='str', choices=['paravirtual', 'hvm'])
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

    owners = module.params.get('owners')
    executable_by = module.params.get('executable_by')
    results = find(
            module,
            connection,
            owners=owners,
            executable_by=executable_by,
            )

    module.exit_json(
            changed=False,
            **results
            )

if __name__ == "__main__":
    main()
