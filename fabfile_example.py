"""
fab deployment script
====================================

"""
import json

from fabric.api import *
import fabric.colors

from fab_deploy import *

def my_site():
	""" Default Configuration """
	env.conf = dict(
        #AWS_ACCESS_KEY_ID     = '',
        #AWS_SECRET_ACCESS_KEY = '',
		INSTANCE_NAME = 'projectname', # Recommend no underscore characters
        PROVIDER = 'ec2_us_east',
        #RACKSPACE_USER = '',     
        #RACKSPACE_KEY  = '',
		REPO = 'http://some.repo.com/projectname/',
	)

my_site()

#--- Set all available hosts
def set_hosts(stage='development'): 
    hosts = []
    PROVIDER = json.loads(open('fabric.conf','r').read()) 
    if stage in PROVIDER['machines']:
        for name in PROVIDER['machines'][stage]: 
            node_dict = PROVIDER['machines'][stage][name]
			if 'public_ip' in node_dict:
                public_ip = node_dict['public_ip']
                for ip in public_ip:            
                    hosts.append('ubuntu@%s' % ip)  
            else:
                fabric.api.warn(fabric.api.yellow('No public IPs found for %s in %s' % (name,stage)))
    env.hosts = hosts
    update_env()

