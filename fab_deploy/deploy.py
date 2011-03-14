import os.path

import fabric.api
import fabric.colors
import fabric.contrib

from fab_deploy.django_commands import syncdb
from fab_deploy.file import link, unlink
from fab_deploy.machine import deploy_nodes,ec2_create_key,ec2_authorize_port
from fab_deploy.server import web_server_setup,web_server_start,web_server_stop
from fab_deploy.system import prepare_server
from fab_deploy.utils import detect_os, run_as
from fab_deploy import vcs
from fab_deploy.virtualenv import pip_install, virtualenv_create, virtualenv

def go(stage="development",tagname="trunk",keyname='aws.ubuntu'):
	""" A convenience method to deploy everything to run a project """

	ec2_create_key(keyname)
	ec2_authorize_port('default','tcp','22')
	ec2_authorize_port('default','tcp','80')
	deploy_nodes(stage,keyname)
	deploy_full(tagname)
	web_server_setup()
	mysql_install()
	mysql_create_user()
	mysql_create_db()
	syncdb()
	web_server_start()

def deploy_full(tagname):
	""" 
	Prepares server, deploys a project with a given tag name, and then makes
	that deployment the active deployment on the server.

	This step is a convenience step and should only be called once when a server
	is set up for the first time.
	
	Before running this command you'll want to run
	fab_deploy.system.create_linux_account and set up an account.
	
	"""
	os_sys = detect_os()
	if not fabric.contrib.console.confirm("Is the OS detected correctly (%s)?" % os_sys, default = False):
		fabric.api.abort(fabric.colors.red("Detection fails. Please set env.conf.OS to correct value."))
	prepare_server()
	deploy_project(tagname)
	make_active(tagname)

def deploy_project(tagname, force = False):
	""" Deploys project on prepared server. """
	make_src_dir()
	tag_dir = os.path.join(fabric.api.env.conf['SRC_DIR'], tagname)
	if fabric.contrib.files.exists(tag_dir):
		if force:
			fabric.api.warn(fabric.colors.yellow('Removing directory %s and all its contents.' % tag_dir))
			fabric.api.sudo('rm -rf %s' % tag_dir)
		else:
			fabric.api.abort(fabric.colors.red('Tagged directory already exists: %s' % tagname))

	if tagname == 'trunk':
		vcs.push(tagname)
	else:
		with fabric.api.lcd('/tmp'):
			vcs.export(tagname, local = True)
		fabric.contrib.project.rsync_project(
			local_dir = os.path.join('/tmp', tagname),
			remote_dir = fabric.api.env.conf['SRC_DIR'])
		fabric.api.local('rm -rf %s' % os.path.join('/tmp', tagname))

	with fabric.api.cd(tag_dir):
		virtualenv_create()
		with virtualenv():
			pip_install()

	fabric.api.sudo('chown -R ubuntu:ubuntu /srv')

def make_src_dir():
	""" Makes the /srv/<project>/ directory and creates the correct permissions """
	fabric.api.sudo('mkdir -p %s' % (fabric.api.env.conf['SRC_DIR']))
	fabric.api.sudo('chown -R ubuntu:ubuntu /srv')

def make_active(tagname):
	""" Make a tag at /srv/<project>/<tagname>  active """
	link(os.path.join(fabric.api.env.conf['SRC_DIR'], tagname),
			'/srv/active', do_unlink = True, silent = True)

def check_active():
	""" Abort if there is no active deployment """
	if not link_exists('/srv/active/'):
		fabric.api.abort(fabric.colors.red('There is no active deployment'))

def undeploy():
	""" Shuts site down. This command doesn't clean everything, e.g.
	user data (database, backups) is preserved. """

	if not fabric.contrib.console.confirm("Do you wish to undeploy host %s?" % fabric.api.env.hosts[0], default = False):
		fabric.api.abort(fabric.colors.red("Aborting."))

	web_server_stop()
	unlink('/srv/active')

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

