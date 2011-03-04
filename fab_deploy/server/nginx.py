import fabric.api

from fab_deploy.package import package_install, package_update
from fab_deploy.system import check_active_deployment, service, link, unlink
from fab_deploy.utils import detect_os

def _nginx_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('dpkg-query --show nginx')
	return output.succeeded

def nginx_install():
	""" Install nginx. """
	if _nginx_is_installed():
		fabric.api.warn(fabric.colors.yellow('Nginx is already installed'))
		return

	os = detect_os()
	options = {'lenny': '-t lenny-backports'}

	fabric.api.sudo('add-apt-repository ppa:nginx/stable')
	package_update()
	package_install(['nginx','libxml2','libxml2-dev'], options.get(os,''))
	#run('rm -f /etc/nginx/sites-enabled/default')

def nginx_setup():
	""" Setup nginx. """
	check_active_deployment()

	nginx_file = '/etc/nginx/nginx.conf'
	unlink(nginx_file,use_sudo=True)
	if fabric.contrib.files.exists(nginx_file):
		fabric.api.sudo('mv %s %s.bkp' % (nginx_file,nginx_file))
	else:
		link('/srv/active/deploy/nginx.conf',nginx_file,use_sudo=True)

def nginx_service(command):
	""" Run a nginx service """
	service('nginx',command)
	nginx_message(command)

def nginx_start():
	""" Start Nginx """
	nginx_service('start')

def nginx_stop():
	""" Stop Nginx """
	nginx_service('stop')

def nginx_restart():
	""" Restarts Nginx """
	nginx_service('restart')

def nginx_message(message):
	""" Print a nginx message """
	fabric.api.puts(fabric.colors.green('nginx %s for %s' % (message,fabric.api.env['host_string'])))

