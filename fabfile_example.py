"""
fab deployment script
====================================

"""
import json, os

from fabric.api import *
import fabric.colors

from fab_deploy import *

def my_site():
	""" Default Configuration """
	env.conf = dict(
		PROVIDER = 'ec2_us_east', # Also can use ec2_us_west
		AWS_ACCESS_KEY_ID     = '',
		AWS_SECRET_ACCESS_KEY = '',
		
		#PROVIDER = 'rackspace',
		#RACKSPACE_USER = '',     
		#RACKSPACE_KEY  = '',
		
		CONF_FILE = os.path.join(os.getcwd(),'fabric.conf'),
		INSTANCE_NAME = 'projectname', # Recommend no underscore characters
		REPO = 'http://some.repo.com/projectname/',
	)

my_site()

#--- Set all available hosts
def set_hosts(stage='development',username='ubuntu',machine=''):
	"""
	The stage specifies which group of machines to set the hosts for

	The username specifies which user to use when setting the hosts

	The machine is optional and can specify a specific machine within
	a stage to set the host for.
	"""
	hosts = []
	PROVIDER = json.loads(open('fabric.conf','r').read()) 
	if stage in PROVIDER['machines']:
		for name in PROVIDER['machines'][stage]:
			if (machine and machine == name) or not machine:
				node_dict = PROVIDER['machines'][stage][name]
				if 'public_ip' in node_dict:
					public_ip = node_dict['public_ip']
					for ip in public_ip:            
						hosts.append('%s@%s' % (username,ip))  
				else:
					fabric.api.warn(fabric.colors.yellow('No public IPs found for %s in %s' % (name,stage)))
			else:
				fabric.api.warn(fabric.colors.yellow('No machines found matching %s in %s' % (machine,stage)))
	env.hosts = hosts
	update_env()

#--- Set up individual hosts
def example():
	env.hosts = ['127.0.0.1',]
	update_env()

