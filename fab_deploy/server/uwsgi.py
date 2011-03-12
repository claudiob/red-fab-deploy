import fabric.api

from fab_deploy.file import link, unlink
from fab_deploy.package import package_install, package_update
from fab_deploy.system import service
from fab_deploy.utils import detect_os

def _uwsgi_is_installed():
	with fabric.api.settings(fabric.api.hide('running','stdout','stderr'), warn_only=True):
		option = fabric.api.run('which uwsgi')
	return option.succeeded

def uwsgi_install():
	""" Install uWSGI. """
	if _uwsgi_is_installed():
		fabric.api.warn(fabric.colors.yellow('uWSGI is already installed'))
		return

	os = detect_os()
	options = {'lenny': '-t lenny-backports'}

	fabric.api.sudo('add-apt-repository ppa:uwsgi/release')
	package_update()
	package_install('uwsgi', options.get(os,''))

def uwsgi_setup():
	""" Setup uWSGI. """
	uwsgi_file = '/etc/uwsgi/uwsgi-python2.6/uwsgi.ini'
	unlink(uwsgi_file,use_sudo=True)
	if fabric.contrib.files.exists(uwsgi_file):
		fabric.api.sudo('mv %s %s.bkp' % (uwsgi_file,uwsgi_file))
	else:
		link('/srv/active/deploy/uwsgi.ini',uwsgi_file,use_sudo=True)

def uwsgi_service(command):
	""" Run a uWSGI service """
	if not _uwsgi_is_installed():
		fabric.api.abort(fabric.colors.yellow('uWSGI must be installed'))
		return
	service('uwsgi-python2.6',command)
	uwsgi_message(command)

def uwsgi_start():
	""" Start uwsgi sockets """
	uwsgi_service('start')

def uwsgi_stop():
	""" Stop uwsgi sockets """
	uwsgi_service('stop')

def uwsgi_restart():
	""" Restarts the uwsgi sockets """
	uwsgi_service('restart')

def uwsgi_message(message):
	""" Print a uWSGI message """
	fabric.api.puts(fabric.colors.green('uWSGI %s for %s' % (message,fabric.api.env['host_string'])))

