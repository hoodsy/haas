"""A switch driver for testing

	 set_access_vlan info will be logged to the console
"""

import logging, sys


def set_access_vlan(port, vlan_id):
	
	# route log handler 
	console = logging.StreamHandler(sys.stdout)
	console.setLevel(logging.DEBUG)

	# init logger and vlan info message
	switchLogger = logging.getLogger('test_switch')
	switchLogger.addHandler(console)
	switchLogger.setLevel(logging.DEBUG)
	vlan_info = 'VLAN_port = '+ str(port) +', VLAN_id = '+ str(vlan_id)

	# log info and debug level information
	switchLogger.debug(vlan_info)
