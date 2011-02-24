from fabric.api import *

from fab_deploy.utils import run_as, upload_config_template
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
		warn('uWSGI is already installed')
		return
	pip('install http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')

def uwsgi_start():
	"""
	Start uwsgi sockets
	"""
	if env.host_string in [env.conf.WEB1]:
		run('''uwsgi -s %(WEB1_INT)s:8001 -p 4 --wsgi-file
			%(dest)s/deploy/django.wsgi -d /tmp/uwsgi.log --gid
			www-data''' % env)
	elif env.host_string in [env.conf.WEB2]:
		run('''uwsgi -s %(WEB2_INT)s:8001 -p 4 --wsgi-file
			%(dest)s/deploy/django.wsgi -d /tmp/uwsgi.log --gid
			www-data''' % env)
	elif env.host_string in [env.conf.DEV]:
		run('''uwsgi -s /tmp/uwsgi.sock -p 4 --wsgi-file
			%(dest)s/deploy/django.wsgi -d /tmp/uwsgi.log --gid
			www-data''' % env)
	else:
		print('No uwsgi start for %(host_string)s' % env)

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
