"""
A switch driver for testing

set_access_vlan debug level info will be logged to console
"""

import logging, sys


def set_access_vlan(port, vlan_id):

	logger = logging.getLogger(__name__)
	logger.debug(' VLAN_port: '+ str(port) +', VLAN_id: '+ str(vlan_id))
