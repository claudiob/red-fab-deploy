import os.path
import time

import fabric.api
import fabric.colors
import fabric.contrib

from fab_deploy.db import *
from fab_deploy.django_commands import syncdb
from fab_deploy.file import link, unlink
from fab_deploy.machine import (generate_config, get_provider_dict, stage_exists,
	ec2_create_key,ec2_authorize_port,
	deploy_nodes,update_nodes)
from fab_deploy.server import *
from fab_deploy.server import web_server_setup,web_server_start,web_server_stop
from fab_deploy.system import prepare_server
from fab_deploy.utils import detect_os, run_as
from fab_deploy import vcs
from fab_deploy.virtualenv import pip_install, virtualenv_create, virtualenv

def go(stage="development",keyname='aws.ubuntu'):
	""" 
	A convenience method to prepare AWS servers.
	
	Use this to create keys, authorize ports, and deploy nodes.
	DO NOT use this step if you've already created keys and opened
	ports on your ec2 instance.
	"""

	# Setup keys and authorize ports
	ec2_create_key(keyname)
	ec2_authorize_port('default','tcp','22')

	# Deploy the nodes for the given stage
	deploy_nodes(stage,keyname)
	time.sleep(30)
	update_nodes()
	
def go_setup(stage="development"):
	"""
	Install the correct services on each machine
	
    $ fab -i deploy/[your private SSH key here] set_hosts go_setup
	"""
	stage_exists(stage)
	PROVIDER = get_provider_dict()
	for name in PROVIDER['machines'][stage]: 
		node_dict = PROVIDER['machines'][stage][name]
		host = node_dict['public_ip'][0]
		if host == fabric.api.env.host:
			prepare_server()
			for service in node_dict['services']:
				if service == 'nginx':
					nginx_install()
					nginx_setup(stage=stage)
				elif service == 'uwsgi':
					uwsgi_install()
					uwsgi_setup()
				elif service == 'mysql':
					mysql_install()
				elif service in ['apache','postgresql']:
					fabric.api.warn(fabric.colors.yellow("%s is not yet available" % service))

def go_deploy(stage="development",tagname="trunk"):
	"""
	Deploy project and make active on any machine with server software
	
    $ fab -i deploy/[your private SSH key here] set_hosts go_deploy
	"""
	stage_exists(stage)
	PROVIDER = get_provider_dict()
	for name in PROVIDER['machines'][stage]: 
		node_dict = PROVIDER['machines'][stage][name]
		host = node_dict['public_ip'][0]
	
		if host == fabric.api.env.host:
			service = node_dict['services']
			if list(set(['nginx','uwsgi','apache']) & set(node_dict['services'])):
				deploy_full(tagname,force=True)
				
def deploy_full(tagname, force=False):
	""" 
	Deploys a project with a given tag name, and then makes
	that deployment the active deployment on the server.
	"""
	deploy_project(tagname, force=force)
	make_active(tagname)

def deploy_project(tagname, force=False):
	""" 
	Deploys a project with a given tag name. 
	"""
	make_src_dir()
	tag_dir = os.path.join(fabric.api.env.conf['SRC_DIR'], tagname)
	if fabric.contrib.files.exists(tag_dir):
		if force:
			fabric.api.warn(fabric.colors.yellow('Removing directory %s and all its contents.' % tag_dir))
			fabric.api.run('rm -rf %s' % tag_dir)
		else:
			fabric.api.abort(fabric.colors.red('Tagged directory already exists: %s' % tagname))

	if tagname == 'trunk':
		vcs.push(tagname)
	else:
		fabric.api.local('rm -rf %s' % os.path.join('/tmp', tagname))
		with fabric.api.lcd('/tmp'):
			vcs.export(tagname, local = True)
		fabric.contrib.project.rsync_project(
			local_dir = os.path.join('/tmp', tagname),
			remote_dir = fabric.api.env.conf['SRC_DIR'],
			extra_opts='--links')
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

