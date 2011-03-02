from fabric.api import *
from fabric.colors import *

from fab_deploy.utils import run_as
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

def uwsgi_setup():
	""" Setup uWSGI. """
	pass

@run_as('root')
def uwsgi_start():
	"""
	Start uwsgi sockets
	"""
	run('uwsgi -s %s:8001 -p 4 --wsgi-file /srv/active/deploy/django_wsgi.py -d /tmp/uwsgi.log --gid www-data' % (env.conf['SRV_INT']))
	print(green('Start uWSGI for %(host_string)s' % env))

@run_as('root')
def uwsgi_stop():
	"""
	Stop uwsgi sockets
	"""
	run('pkill uwsgi')

def uwsgi_restart():
	"""
	Restarts the uwsgi sockets.
	"""
	uwsgi_stop()
	uwsgi_start()

