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
        PROVIDER = 'ec2_us_east', # Also use ec2_us_west
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
def set_hosts(stage='development',username='ubuntu'): 
    hosts = []
    PROVIDER = json.loads(open('fabric.conf','r').read()) 
    if stage in PROVIDER['machines']:
        for name in PROVIDER['machines'][stage]: 
            node_dict = PROVIDER['machines'][stage][name]
			if 'public_ip' in node_dict:
                public_ip = node_dict['public_ip']
                for ip in public_ip:            
                    hosts.append('%s@%s' % (username,ip))  
            else:
                fabric.api.warn(fabric.colors.yellow('No public IPs found for %s in %s' % (name,stage)))
    env.hosts = hosts
    update_env()

#--- Set up individual hosts
def example():
	env.hosts = ['127.0.0.1',]
	update_env()

