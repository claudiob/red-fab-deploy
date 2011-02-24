from fabric.api import *

from fab_deploy.utils import detect_os, run_as, upload_config_template
from fab_deploy.system import aptitude_install, aptitude_update

def _nginx_is_installed():
	with settings(hide('stderr'), warn_only=True):
		output = run('dpkg-query --show nginx')
	return output.succeeded

@run_as('root')
def nginx_install():
	""" Install nginx. """
	if _nginx_is_installed():
		warn('Nginx is already installed')
		return
	
	os = detect_os()
	options = {'lenny': '-t lenny-backports'}

	sudo('add-apt-repository ppa:nginx/stable')
	aptitude_update()
	aptitude_install('nginx libxml2 libxml2-dev', options.get(os,''))
	run('rm -f /etc/nginx/sites-enabled/default')

@run_as('root')
def nginx_setup():
	""" Updates nginx config and restarts nginx """
	run('cd /opt/nginx/conf')
	sudo('mv nginx.conf nginx.conf.backup')
	if env.host_string in [env.LOAD1]:
		sudo('ln -s %(dest)s/deploy/nginx.conf')
	elif env.host_string in [env.DEV]:
		sudo('ln -s %(dest)s/deploy/nginx.conf.dev')
	else:
		print('No nginx link for %(host_string)s' % env)

def nginx_start():
	""" Start Nginx. """
	if env.host_string in [env.LOAD1]:
		run('/opt/nginx/sbin/nginx')
	else:
		print('No nginx start for %(host_string)s' % env)

def nginx_stop():
	""" Stop Nginx. """
	run('pkill nginx')

def nginx_restart():
	""" Restarts Nginx. """
	nginx_stop()
	nginx_start()

