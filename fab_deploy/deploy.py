import os.path

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

from fab_deploy.server import *
from fab_deploy.system import prepare_server, make_src_dir, make_active
from fab_deploy.utils import detect_os, run_as
from fab_deploy import vcs
from fab_deploy.virtualenv import pip_install, virtualenv_create, virtualenv

def full_deploy(tagname):
	""" 
	Prepares server, deploys a project with a given tag name, and then makes
	that deployment the active deployment on the server.

	This step is a convenience step and should only be called once when a server
	is set up for the first time.
	
	Before running this command you'll want to run
	fab_deploy.system.create_linux_account and set up an account.
	
	"""
	os_sys = detect_os()
	if not confirm("Is the OS detected correctly (%s)?" % os_sys, default=False):
		abort(red("Detection fails. Please set env.conf.OS to correct value."))
	prepare_server()
	deploy_project(tagname)
	make_active(tagname)

def deploy_project(tagname):
	""" Deploys project on prepared server. """
	make_src_dir()
	tag_dir = os.path.join(env.conf['SRC_DIR'],tagname)
	if exists(tag_dir):
		abort(red('Tagged directory already exists: %s' % tagname))

	vcs.export(tagname)

	with cd(tag_dir):
		virtualenv_create()
		with virtualenv():
			pip_install()

	sudo('chown -R www-data:www-data /srv')
	sudo('chmod -R g+w /srv')

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

