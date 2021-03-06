# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

from nose.plugins.skip import SkipTest
if sys.version_info < (2, 7):
    raise SkipTest("F5 Ansible modules require Python >= 2.7")

from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch, Mock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.module_utils.f5_utils import AnsibleF5Client
from ansible.module_utils.f5_utils import F5ModuleError

try:
    from library.bigip_vcmp_guest import Parameters
    from library.bigip_vcmp_guest import ModuleManager
    from library.bigip_vcmp_guest import ArgumentSpec
    from ansible.module_utils.f5_utils import iControlUnexpectedHTTPError
except ImportError:
    try:
        from ansible.modules.network.f5.bigip_vcmp_guest import Parameters
        from ansible.modules.network.f5.bigip_vcmp_guest import ModuleManager
        from ansible.modules.network.f5.bigip_vcmp_guest import ArgumentSpec
        from ansible.module_utils.f5_utils import iControlUnexpectedHTTPError
    except ImportError:
        raise SkipTest("F5 Ansible modules require the f5-sdk Python library")

fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            initial_image='BIGIP-12.1.0.1.0.1447-HF1.iso',
            mgmt_network='bridged',
            mgmt_address='1.2.3.4/24',
            vlans=[
                'vlan1',
                'vlan2'
            ]
        )

        p = Parameters(args)
        assert p.initial_image == 'BIGIP-12.1.0.1.0.1447-HF1.iso'
        assert p.mgmt_network == 'bridged'

    def test_module_parameters_mgmt_bridged_without_subnet(self):
        args = dict(
            mgmt_network='bridged',
            mgmt_address='1.2.3.4'
        )

        p = Parameters(args)
        assert p.mgmt_network == 'bridged'
        assert p.mgmt_address == '1.2.3.4/24'

    def test_module_parameters_mgmt_address_cidr(self):
        args = dict(
            mgmt_network='bridged',
            mgmt_address='1.2.3.4/24'
        )

        p = Parameters(args)
        assert p.mgmt_network == 'bridged'
        assert p.mgmt_address == '1.2.3.4/24'

    def test_module_parameters_mgmt_address_subnet(self):
        args = dict(
            mgmt_network='bridged',
            mgmt_address='1.2.3.4/255.255.255.0'
        )

        p = Parameters(args)
        assert p.mgmt_network == 'bridged'
        assert p.mgmt_address == '1.2.3.4/24'

    def test_module_parameters_mgmt_route(self):
        args = dict(
            mgmt_address='1.2.3.4'
        )

        p = Parameters(args)
        assert p.mgmt_route == '1.2.3.4'

    def test_module_parameters_vcmp_software_image_facts(self):
        # vCMP images may include a forward slash in their names. This is probably
        # related to the slots on the system, but it is not a valid value to specify
        # that slot when providing an initial image
        args = dict(
            initial_image='BIGIP-12.1.0.1.0.1447-HF1.iso/1',
        )

        p = Parameters(args)
        assert p.initial_image == 'BIGIP-12.1.0.1.0.1447-HF1.iso'

    def test_api_parameters(self):
        args = dict(
            initialImage="BIGIP-tmos-tier2-13.1.0.0.0.931.iso",
            managementGw="2.2.2.2",
            managementIp="1.1.1.1/24",
            managementNetwork="bridged",
            state="deployed",
            vlans=[
                "/Common/vlan1",
                "/Common/vlan2"
            ]
        )

        p = Parameters(args)
        assert p.initial_image == 'BIGIP-tmos-tier2-13.1.0.0.0.931.iso'
        assert p.mgmt_route == '2.2.2.2'
        assert p.mgmt_address == '1.1.1.1/24'
        assert '/Common/vlan1' in p.vlans
        assert '/Common/vlan2' in p.vlans


@patch('ansible.module_utils.f5_utils.AnsibleF5Client._get_mgmt_root',
       return_value=True)
class TestManager(unittest.TestCase):

    def test_create(self, *args):
        raise Exception('You must write a creation test')
