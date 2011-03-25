"""
fab deployment script
====================================

"""
import simplejson
from fabric.api import *
import fabric.colors
from fab_deploy import *

def my_site():
    """ Default Configuration """
    env.conf = dict(
        AWS_ACCESS_KEY_ID     = '%(AWS_ACCESS_KEY_ID)s',
        AWS_SECRET_ACCESS_KEY = '%(AWS_SECRET_ACCESS_KEY)s',
        INSTANCE_NAME         = '%(INSTANCE_NAME)s', # Recommend no underscores
        PROVIDER              = '%(PROVIDER)s',
        RACKSPACE_USER        = '%(RACKSPACE_USER)s',     
        RACKSPACE_KEY         = '%(RACKSPACE_KEY)s',
        REPO                  = '%(REPO)s',
    )

my_site()

#--- Set all available hosts
def set_hosts(stage='development'): 
    hosts = []
    PROVIDER = simplejson.loads(open('fabric.conf','r').read()) 
    if stage in PROVIDER['machines']:
        for name in PROVIDER['machines'][stage]: 
            node_dict = PROVIDER['machines'][stage][name]
            if 'public_ip' in node_dict:
                public_ip = node_dict['public_ip']
                for ip in public_ip:            
                    hosts.append('ubuntu@%%s' %% ip)  
            else:
                fabric.api.warn(fabric.api.yellow('No public IPs found for %%s in %%s' %% (name,stage)))
    env.hosts = hosts
    update_env()
