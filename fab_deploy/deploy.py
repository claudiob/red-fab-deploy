import os.path

import fabric.api

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
	if not fabric.contrib.console.confirm("Is the OS detected correctly (%s)?" % os_sys, default=False):
		abort(fabric.colors.red("Detection fails. Please set env.conf.OS to correct value."))
	prepare_server()
	deploy_project(tagname)
	make_active(tagname)

def deploy_project(tagname):
	""" Deploys project on prepared server. """
	make_src_dir()
	tag_dir = os.path.join(fabric.api.env.conf['SRC_DIR'],tagname)
	if fabric.contrib.files.exists(tag_dir):
		abort(fabric.colors.red('Tagged directory already exists: %s' % tagname))

	if tagname == 'trunk':
		vcs.push(tagname)
	else:
		vcs.export(tagname)

	with fabric.api.cd(tag_dir):
		virtualenv_create()
		with virtualenv():
			pip_install()

	fabric.api.sudo('chown -R www-data:www-data /srv')
	fabric.api.sudo('chmod -R g+w /srv')

#def undeploy():
#	""" Shuts site down. This command doesn't clean everything, e.g.
#	user data (database, backups) is preserved. """
#
#	if not fabric.contrib.console.confirm("Do you wish to undeploy host %s?" % fabric.api.env.hosts[0], default=False):
#		abort(fabric.colors.red("Aborting."))
#
#	@run_as('root')
#	def wipe_web():
#		fabric.api.run('rm -f /etc/nginx/sites-enabled/%s' % fabric.api.env.conf['INSTANCE_NAME'])
#		fabric.api.run('a2dissite %s' % fabric.api.env.conf['INSTANCE_NAME'])
#		fabric.api.run('invoke-rc.d nginx reload')
#		fabric.api.run('invoke-rc.d apache2 reload')
#
#	wipe_web()
#	fabric.api.run('rm -rf %s' % fabric.api.env.conf['SRC_DIR'])
#	for folder in ['bin', 'include', 'lib', 'src']:
#		fabric.api.run('rm -rf %s/%s' % (fabric.api.env.conf['ENV_DIR'], folder))

