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
		REPO = 'http://some.repo.com/project_name/trunk',
		SERVERS = {
		}
	)
	update_env()

my_site()

#--- Servers
def dev():
	"""
	Include all development servers
	"""
	env.hosts = [env.conf['DEV']]
	if 'DEV_PASSWD' in env:
		env.password = env.conf['DEV_PASSWD']

def load1():
	"""
	Include load balancer
	"""
	env.hosts = [env.conf['LOAD1']]
	if 'LOAD1_PASSWD' in env:
		env.password = env.conf['LOAD1_PASSWD']

def web1():
	"""
	Include web server 1
	"""
	env.hosts = [env.conf['WEB1']]
	if 'WEB1_PASSWD' in env:
		env.password = env.conf['WEB1_PASSWD']

def web2():
	"""
	Include web server 2
	"""
	env.hosts = [env.conf['WEB2']]
	if 'WEB2_PASSWD' in env:
		env.password = env.conf['WEB2_PASSWD']

def db1():
	"""
	Include db server 1
	"""
	env.hosts = [env.conf['DB1']]
	if 'DB1_PASSWD' in env:
		env.password = env.conf['DB1_PASSWD']

def db2():
	"""
	Include db server 2
	"""
	env.hosts = [env.conf['DB2']]
	if 'DB2_PASSWD' in env:
		env.password = env.conf['DB2_PASSWD']

