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

#--- Set up individual hosts
def example():
	env.hosts = ['127.0.0.1',]
	update_env()

