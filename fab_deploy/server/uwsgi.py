from fabric.api import *
from fabric.colors import *

from fab_deploy.utils import run_as
from fab_deploy.system import aptitude_install
from fab_deploy.virtualenv import pip

def _uwsgi_is_installed():
	with settings(hide('stderr'), warn_only=True):
		option = run('which uwsgi')
	return option.succeeded

@run_as('root')
def uwsgi_install():
	""" Install uWSGI. """
	if _uwsgi_is_installed():
		warn(yellow('uWSGI is already installed'))
		return
	pip('install http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')

@run_as('root')
def uwsgi_setup():
	""" Setup uWSGI. """
	pass

@run_as('root')
def uwsgi_start():
	"""
	Start uwsgi sockets
	"""
	run('uwsgi -s %s:8001 -p 4 --wsgi-file %s/deploy/django.wsgi -d /tmp/uwsgi.log --gid www-data' % (env.conf['SERVERS']['DEV_INT'],env.conf['SRC_DIR']))

@run_as('root')
def uwsgi_stop():
	"""
	Stop uwsgi sockets
	"""
	run('pkill uwsgi')

@run_as('root')
def uwsgi_restart():
	"""
	Restarts the uwsgi sockets.
	"""
	uwsgi_stop()
	uwsgi_start()

