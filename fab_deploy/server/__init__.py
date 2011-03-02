from fab_deploy.server.apache import (apache_install, apache_setup,
	apache_start, apache_stop, apache_restart, 
	apache_touch_wsgi, apache_make_wsgi,
	apache_make_config, apache_setup_locale, )
from fab_deploy.server.nginx import (nginx_install, nginx_setup,
	nginx_start, nginx_stop, nginx_restart, )
from fab_deploy.server.uwsgi import (uwsgi_install, uwsgi_setup,
	uwsgi_start, uwsgi_stop, uwsgi_restart, )

def web_server_setup(tagname):
	""" Sets up a web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_install()
		apache_setup(tagname)
	elif env.conf['SERVER_TYPE'] == 'nginx':	
		nginx_install()
		nginx_setup(tagname)
		uwsgi_install()
		uwsgi_setup()

def web_server_start():
	""" Starts up a web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_start()
	elif env.conf['SERVER_TYPE'] == 'nginx':	
		nginx_start()
		uwsgi_start()

def web_server_stop():
	""" Stops the web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_stop()
	elif env.conf['SERVER_TYPE'] == 'nginx':
		uwsgi_stop()
		nginx_stop()

def web_server_restart():
	""" Restarts the web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_restart()
	elif env.conf['SERVER_TYPE'] == 'nginx':
		nginx_restart()

def web_server_touch():
	""" Touches the web server causing reload. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_touch_wsgi()
	elif env.conf['SERVER_TYPE'] == 'nginx':
		uwsgi_restart()

