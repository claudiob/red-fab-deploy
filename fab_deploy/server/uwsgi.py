import fabric.api
import fabric.contrib
import os

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

def uwsgi_setup(stage=''):
	""" Setup uWSGI. """
	
	# Service script
	uwsgi_service_script = '/etc/init.d/uwsgi'
	if fabric.contrib.files.exists(uwsgi_service_script):
		fabric.api.sudo('mv %s %s.bkp' % (uwsgi_service_script, uwsgi_service_script))
	fabric.api.put(os.path.join(fabric.api.env.conf['FILES'], 'uwsgi_init.sh'), uwsgi_service_script, use_sudo=True)
	fabric.api.sudo('chmod 755 %s' % uwsgi_service_script)
	fabric.api.sudo('chown root:root %s' % uwsgi_service_script)

	# INI File
	fabric.api.sudo('mkdir -p /etc/uwsgi')
	uwsgi_file = '/etc/uwsgi/uwsgi.ini'
	unlink(uwsgi_file, use_sudo=True)
	if fabric.contrib.files.exists(uwsgi_file):
		fabric.api.sudo('mv %s %s.bkp' % (uwsgi_file, uwsgi_file))
	if stage:
		stage = '.%s' % stage
	link('/srv/active/deploy/uwsgi%s.ini' % stage, uwsgi_file, use_sudo = True)

	# Log File
	fabric.api.sudo('mkdir -p /var/log/uwsgi')
	fabric.api.sudo('touch /var/log/uwsgi/errors.log')
	fabric.api.sudo('chmod -R a+w /var/log/uwsgi')

def uwsgi_service(command):
	""" Run a uWSGI service """
	if not _uwsgi_is_installed():
		fabric.api.warn(fabric.colors.yellow('uWSGI must be installed'))
		return
	service('uwsgi', command)
	uwsgi_message(command)

def uwsgi_start():
	uwsgi_service('start')

def uwsgi_stop():
	uwsgi_service('stop')

def uwsgi_restart():
	uwsgi_service('restart')

def uwsgi_message(message):
	""" Print a uWSGI message """
	fabric.api.puts(fabric.colors.green('uWSGI %s for %s' % (message, fabric.api.env['host_string'])))

