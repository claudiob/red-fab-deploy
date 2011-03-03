"""
fab deployment script
====================================

"""
from fabric.api import *
from fabric.contrib.project import *

from fab_deploy import *

def my_site():
	""" Default Configuration """
	env.conf = dict(
		INSTANCE_NAME = 'project_name',
		REPO = 'http://some.repo.com/project_name/',
		SERVERS = {
			'DEV'          : 'ubuntu@some.external.ip.address',
		}
	)

my_site()

#--- Servers
def dev():
	"""
	Include all development servers
	"""
	env.hosts = [env.conf['SERVERS']['DEV']]
	update_env()

