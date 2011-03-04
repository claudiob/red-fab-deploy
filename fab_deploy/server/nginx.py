import fabric.api

from fab_deploy.package import package_install, package_update
from fab_deploy.utils import detect_os

def _nginx_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = run('dpkg-query --show nginx')
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
	""" Updates nginx config and restarts nginx """
	if not fabric.contrib.files.exists('/srv/active/'):
		fabric.api.warn(fabric.colors.yellow('There is no active deployment'))
		return

	if fabric.contrib.files.exists('/etc/nginx/nginx.conf.bkp'):
		fabric.api.warn(fabric.colors.yellow('Nginx has already been set up'))
		return
	else:
		fabric.api.sudo('mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bkp')
		fabric.api.sudo('ln -s /srv/active/deploy/nginx.conf /etc/nginx/nginx.conf')

def nginx_start():
	""" Start Nginx. """
	fabric.api.sudo('service nginx start')
	fabric.api.puts(fabric.colors.green('Start nginx for %(host_string)s' % fabric.api.env))

def nginx_stop():
	""" Stop Nginx. """
	fabric.api.sudo('service nginx stop')

def nginx_restart():
	""" Restarts Nginx. """
	fabric.api.sudo('service nginx restart')

