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
			'DEV'          : 'some.external.ip.address',
			'DEV_INT'      : 'some.internal.ip.address',
			'DEV_PASSWD'   : 'password',
		}
	)

my_site()

#--- Servers
def dev():
	"""
	Include all development servers
	"""
	env.hosts = [env.conf['SERVERS']['DEV']]
	if 'DEV_PASSWD' in env.conf['SERVERS']:
		env.password = env.conf['SERVERS']['DEV_PASSWD']
	if 'DEV_INT' in env.conf['SERVERS']:
		env.conf['SRV_INT'] = env.conf['SERVERS']['DEV_INT']
	update_env()

