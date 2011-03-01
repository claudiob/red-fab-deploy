import os.path

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists,upload_template

from fab_deploy.django_commands import compress, migrate, syncdb, test
from fab_deploy.server import *
from fab_deploy.system import prepare_server
from fab_deploy.utils import delete_pyc, detect_os, run_as
from fab_deploy import vcs
from fab_deploy.virtualenv import (pip_install, pip_update, 
	virtualenv_create, virtualenv)

def full_deploy(tagname):
	""" Prepares server and deploys the project. """
	os = detect_os()
	if not confirm("Is the OS detected correctly (%s)?" % os, default=False):
		abort(red("Detection fails. Please set env.conf.OS to correct value."))
	prepare_server()
	deploy_project(tagname)

def deploy_project(tagname):
	""" Deploys project on prepared server. """
	make_src_dir()
	tag_dir = os.path.join(env.conf['SRC_DIR'],tagname)
	if exists(tag_dir):
		abort(red('Tagged directory already exists: %s' % tagname))

	export(tagname)

	with cd(tag_dir):
		virtualenv_create()
		with virtualenv():
			pip_install()
		#syncdb()
		# load sql database dump
	#setup_web_server()

@run_as('root')
def make_src_dir():
	run('mkdir -p %s' % env.conf['SRC_DIR'])
	run('chmod a+w %s' % env.conf['SRC_DIR'])

def setup_web_server():
	""" Sets up a web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_install()
		apache_setup()
	elif env.conf['SERVER_TYPE'] == 'nginx':	
		nginx_install()
		nginx_setup()
		uwsgi_install()
		uwsgi_setup()

def start_web_server():
	""" Starts up a web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_start()
	elif env.conf['SERVER_TYPE'] == 'nginx':	
		nginx_start()
		uwsgi_start()

def stop_web_server():
	""" Stops the web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_stop()
	elif env.conf['SERVER_TYPE'] == 'nginx':
		uwsgi_stop()
		nginx_stop()

def restart_web_server():
	""" Restarts the web server. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_restart()
	elif env.conf['SERVER_TYPE'] == 'nginx':
		nginx_restart()

def touch_web_server():
	""" Touches the web server causing reload. """
	if env.conf['SERVER_TYPE'] == 'apache':
		apache_touch_wsgi()
	elif env.conf['SERVER_TYPE'] == 'nginx':
		uwsgi_restart()

def up(tagname):
	""" Runs vcs ``update`` command on server """
#	delete_pyc()
	vcs.up(tagname)
#	compress()
#	touch_web_server()

def push(tagname):
	""" Runs vcs ``checkout`` command on server """
	vcs.push(tagname)

def export(tagname):
	""" Runs vcs ``export`` command on server """
	vcs.export(tagname)

#def push(*args):
#	''' Run it instead of your VCS push command.
#
#	Arguments:
#
#	* notest - don't run tests
#	* syncdb - run syncdb before code reloading
#	* migrate - run migrate before code reloading
#	* pip_update - run pip_update before code reloading
#	* norestart - do not reload source code
#	'''
#	allowed_args = set(['force', 'notest', 'syncdb', 'migrate', 'pip_update', 'norestart'])
#	for arg in args:
#		if arg not in allowed_args:
#			puts('Invalid argument: %s' % arg)
#			puts('Valid arguments are: %s' % allowed_args)
#			return
#
#	vcs.push()
#	delete_pyc()
#	with cd('src/'+env.conf['INSTANCE_NAME']):
#		vcs.up()
#
#	if 'pip_update' in args:
#		pip_update()
#	if 'syncdb' in args:
#		syncdb()
#	if 'migrate' in args:
#		migrate()
#	compress()
#	if 'norestart' not in args:
#		touch_web_server()
#	if 'notest' not in args:
#		test()

#def make_clone(tagname):
#	""" Creates repository clone on remote server. """
#	run('mkdir -p '+ env.conf['SRC_DIR'])
#	with cd(env.conf['SRC_DIR']):
#		with settings(warn_only=True):
#			svn.init()
#	svn.push(tagname)
#	with cd(env.conf['SRC_DIR']):
#		vcs.up(tagname)
#	svn.configure()

#def update_django_config(restart=True):
#	""" Updates :file:`config.py` on server (using :file:`config.server.py`) """
#	
#	# red typically makes it's own server files using the name of the server
#	# uploading a template is not the right approach right now
#	# TODO: Revisit this code to see if it can be useful.
#	upload_template('config.server.py', '%s/config.py' % env.conf['SRC_DIR'], env.conf, True)
#	if restart:
#		touch_web_server()

#def undeploy():
#	""" Shuts site down. This command doesn't clean everything, e.g.
#	user data (database, backups) is preserved. """
#
#	if not confirm("Do you wish to undeploy host %s?" % env.hosts[0], default=False):
#		abort(red("Aborting."))
#
#	@run_as('root')
#	def wipe_web():
#		run('rm -f /etc/nginx/sites-enabled/'+env.conf['INSTANCE_NAME'])
#		run('a2dissite ' + env.conf['INSTANCE_NAME'])
#		run('invoke-rc.d nginx reload')
#		run('invoke-rc.d apache2 reload')
#
#	wipe_web()
#	run('rm -rf %s' % env.conf['SRC_DIR'])
#	for folder in ['bin', 'include', 'lib', 'src']:
#		run('rm -rf %s' % env.conf['ENV_DIR'] + '/' + folder)
#
