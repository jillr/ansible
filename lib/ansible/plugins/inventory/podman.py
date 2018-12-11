# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: podman
    plugin_type: inventory
    author:
     - Jill Rouleau <@jillr>
    
    short_description: Podman inventory source
    
    description:
      - Fetch containers from Podman via Podman cli or Varlink API
    
    options:
      plugin:
         description: token that ensures this is a source file for the 'podman'
         plugin.
      mechanism:
        description: Whether to use the Podman cli or Varlink to obtain data
        default: podman
        choices: ['varlink', 'podman']  
    
    requirements:
    - "python >= 2.7"
    - "varlink >= 29.0.0" # TODO: maybe optional?
'''

EXAMPLES = '''
# File must be named podman.yml or podman.yaml
'''

import json
import subprocess
import varlink

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = 'podman'

    def verify_file(self, path):
        """
        return true/false if this is possibly a valid file for this plugin
        to consume
        """
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies file exists and is readable by current user
            if path.endswith(('podman.yaml', 'podman.yml', 'vbox.yaml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        config = self._read_config_data(self, path)

        mechanism = self.get_option('mechanism')
        if 'varlink' in mechanism:
            return_data = self.varlink_inventory()
        else:
            return_data = self.podman_cli_inventory()

        for container in return_data:
            self.inventory.add_hosts(container['Name'])

    def varlink_inventory(self):
        """
        connect to varlink socket and query containers
        Extremely WIP atm
        :return:
        """
        varlink_conn = varlink.Client(self.get_option('unix_socket' +
                                                      '.ListContainers'))
        return_data = varlink_conn
        return return_data

    def podman_cli_inventory(self):
        cmd = ['podman', 'container', 'ls', '--format=json']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        podman_out, podman_err = p.communicate()
        container_list = json.loads(podman_out)

        return container_list

