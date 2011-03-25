import fabric.api

from fab_deploy.server.apache import (apache_install, apache_setup,
	apache_start, apache_stop, apache_restart, apache_touch_wsgi,)
from fab_deploy.server.nginx import (nginx_install, nginx_setup,
	nginx_start, nginx_stop, nginx_restart, )
from fab_deploy.server.uwsgi import (uwsgi_install, uwsgi_setup,
	uwsgi_start, uwsgi_stop, uwsgi_restart, )

def web_server_setup(stage=''):
	""" Sets up a web server. """
	if fabric.api.env.conf['SERVER_TYPE'] == 'apache':
		apache_install()
		apache_setup()
	elif fabric.api.env.conf['SERVER_TYPE'] == 'nginx':
		nginx_install()
		nginx_setup(stage=stage)
		uwsgi_install()
		uwsgi_setup(stage = stage)

def web_server_start():
	""" Starts up a web server. """
	if fabric.api.env.conf['SERVER_TYPE'] == 'apache':
		apache_start()
	elif fabric.api.env.conf['SERVER_TYPE'] == 'nginx':	
		nginx_start()
		uwsgi_start()

def web_server_stop():
	""" Stops the web server. """
	if fabric.api.env.conf['SERVER_TYPE'] == 'apache':
		apache_stop()
	elif fabric.api.env.conf['SERVER_TYPE'] == 'nginx':
		uwsgi_stop()
		nginx_stop()

def web_server_restart():
	""" Restarts the web server. """
	if fabric.api.env.conf['SERVER_TYPE'] == 'apache':
		apache_restart()
	elif fabric.api.env.conf['SERVER_TYPE'] == 'nginx':
		nginx_restart()
		uwsgi_restart()

def web_server_touch(stage=''):
	""" Touches the web server causing reload. """
	if fabric.api.env.conf['SERVER_TYPE'] == 'apache':
		apache_touch_wsgi()
	elif fabric.api.env.conf['SERVER_TYPE'] == 'nginx':
		uwsgi_restart(stage=stage)

