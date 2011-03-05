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
			'DEV'   : 'ubuntu@some.external.ip.address',
			'LOAD1' : 'ubuntu@some.external.ip.address',
			'WEB1'  : 'ubuntu@some.external.ip.address',
			'WEB2'  : 'ubuntu@some.external.ip.address',
			'DB1'   : 'ubuntu@some.external.ip.address',
			'DB2'   : 'ubuntu@some.external.ip.address',

			'CHRIS' : 'ubuntu@some.internal.ip.address',
		}
	)

	env.roledefs = {
        'devservers'  : [
            env.conf['SERVERS']['DEV']       
            ],
        'loadservers' : [
            env.conf['SERVERS']['LOAD1']     
            ],
        'webservers'  : [
            env.conf['SERVERS']['WEB1']      
            env.conf['SERVERS']['WEB2']      
            ],
        'dbservers'   : [
            env.conf['SERVERS']['DB1']       
            env.conf['SERVERS']['DB2']       
            ],
        'developers'  : [
            env.conf['SERVERS']['CHRIS']       
            ],
	}

my_site()

#--- Roledefs
def devservers():
    env.hosts = env.roledefs['devservers']
    update_env()

def loadservers():
    env.hosts = env.roledefs['loadservers']
    update_env()

def webservers():
    env.hosts = env.roledefs['webservers']
    update_env()

def dbservers():
    env.hosts = env.roledefs['dbservers']
    update_env()

def developers():
    env.hosts = env.roledefs['developers']
    update_env()

#--- Servers
def dev():
	env.hosts = [env.conf['SERVERS']['DEV']]
	update_env()

def chris()
	env.hosts = [env.conf['SERVERS']['CHRIS']]
	update_env()

