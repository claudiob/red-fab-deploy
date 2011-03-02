from fabric.api import *
from fabric.colors import *
from fabric.contrib.files import exists

from fab_deploy.utils import detect_os, run_as
from fab_deploy.system import aptitude_install, aptitude_update

def _nginx_is_installed():
	with settings(hide('stderr'), warn_only=True):
		output = run('dpkg-query --show nginx')
	return output.succeeded

@run_as('root')
def nginx_install():
	""" Install nginx. """
	if _nginx_is_installed():
		warn(yellow('Nginx is already installed'))
		return

	os = detect_os()
	options = {'lenny': '-t lenny-backports'}

	sudo('add-apt-repository ppa:nginx/stable')
	aptitude_update()
	aptitude_install('nginx libxml2 libxml2-dev', options.get(os,''))
	run('rm -f /etc/nginx/sites-enabled/default')

@run_as('root')
def nginx_setup(tagname):
	""" Updates nginx config and restarts nginx """
	if not exists('/srv/active/'):
		warn(yellow('There is no active deployment'))
		return

	if exists('/etc/nginx/nginx.conf.bkp'):
		warn(yellow('Nginx has already been set up'))
	else:
		run('mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bkp')
	
	run('ln -s /srv/active/deploy/nginx.conf /etc/nginx/nginx.conf')

@run_as('root')
def nginx_start():
	""" Start Nginx. """
	run('/usr/sbin/nginx')
	print('Start nginx for %(host_string)s' % env)

@run_as('root')
def nginx_stop():
	""" Stop Nginx. """
	run('pkill nginx')

def nginx_restart():
	""" Restarts Nginx. """
	nginx_stop()
	nginx_start()

