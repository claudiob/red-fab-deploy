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

	fabric.api.sudo('mkdir -p /etc/uwsgi')
	fabric.api.sudo('mkdir -p /var/log/uwsgi')
	fabric.api.sudo('touch /var/log/uwsgi/errors.log')
	fabric.api.sudo('chown www-data:www-data -R /var/log/uwsgi')

	uwsgi_file = '/etc/uwsgi/uwsgi.ini'
	unlink(uwsgi_file, use_sudo = True, silent=True)
	if fabric.contrib.files.exists(uwsgi_file):
		fabric.api.sudo('mv %s %s.bkp' % (uwsgi_file, uwsgi_file))
	link('/srv/active/deploy/uwsgi.ini', uwsgi_file, use_sudo = True)

def uwsgi_start():
	""" Start uwsgi sockets """
	if not _uwsgi_is_installed():
		fabric.api.abort(fabric.colors.red('uWSGI must be installed'))
		return

	fabric.api.sudo('uwsgi --ini /srv/active/deploy/uwsgi.ini')
	uwsgi_message('Start')

def uwsgi_stop():
	""" Stop uwsgi sockets """
	if not _uwsgi_is_installed():
		fabric.api.abort(fabric.colors.red('uWSGI must be installed'))
		return

	fabric.api.sudo('pkill -9 uwsgi')
	uwsgi_message('Stop')

def uwsgi_restart():
	""" Restarts the uwsgi sockets """
	uwsgi_stop()
	uwsgi_start()
	uwsgi_message('Restarted')

def uwsgi_message(message):
	""" Print a uWSGI message """
	fabric.api.puts(fabric.colors.green('uWSGI %s for %s' % (message, fabric.api.env['host_string'])))

