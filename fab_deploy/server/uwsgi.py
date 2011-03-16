import fabric.api
import fabric.contrib

from fab_deploy.file import link, unlink
from fab_deploy.package import package_install, package_update
from fab_deploy.system import service
from fab_deploy.utils import detect_os

def _uwsgi_is_installed():
	with fabric.api.settings(fabric.api.hide('running', 'stdout', 'stderr'), warn_only = True):
		option = fabric.api.run('which uwsgi')
	return option.succeeded

def uwsgi_install():
	""" Install uWSGI. """
	if _uwsgi_is_installed():
		fabric.api.warn(fabric.colors.yellow('uWSGI is already installed'))
		return

	package_install('libxml2','libxml2-dev')
	fabric.api.sudo('pip install http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')

def uwsgi_setup():
	""" Setup uWSGI. """
	fabric.api.sudo('mkdir -p /var/log/uwsgi')
	fabric.api.sudo('touch /var/log/uwsgi/errors.log')
	fabric.api.sudo('chown www-data:www-data -R /var/log/uwsgi')

def uwsgi_start(stage=''):
	""" Start uwsgi sockets """
	if not _uwsgi_is_installed():
		fabric.api.warn(fabric.colors.yellow('uWSGI must be installed'))
		return

	if stage:
		stage = '.%s' % stage
	fabric.api.sudo('uwsgi --ini /srv/active/deploy/uwsgi.ini%s' % stage)
	uwsgi_message('Start')

def uwsgi_stop():
	""" Stop uwsgi sockets """
	if not _uwsgi_is_installed():
		fabric.api.warn(fabric.colors.yellow('uWSGI must be installed'))
		return

	with fabric.api.settings(warn_only=True):
		fabric.api.sudo('pkill -9 uwsgi')
	uwsgi_message('Stop')

def uwsgi_restart(stage=''):
	""" Restarts the uwsgi sockets """
	if not _uwsgi_is_installed():
		fabric.api.warn(fabric.colors.yellow('uWSGI must be installed'))
		return

	uwsgi_stop()
	uwsgi_start(stage=stage)
	uwsgi_message('Restarted')

def uwsgi_message(message):
	""" Print a uWSGI message """
	fabric.api.puts(fabric.colors.green('uWSGI %s for %s' % (message, fabric.api.env['host_string'])))

