"""
A switch driver for testing

set_access_vlan debug level info will be logged to console
"""

import logging, sys


def set_access_vlan(port, vlan_id):

	logging.basicConfig(level=logging.DEBUG)
	logger = logging.getLogger(__name__)
	logger.debug('A hopefully helpful message')
