import os.path
import time

import fabric.api
import fabric.colors
import fabric.contrib

from fab_deploy.db import *
from fab_deploy.django_commands import syncdb
from fab_deploy.file import link, unlink
from fab_deploy.machine import (generate_config, get_provider_dict, stage_exists,
	ec2_create_key, ec2_authorize_port,
	deploy_nodes, update_nodes)
from fab_deploy.server import *
from fab_deploy.system import get_hostname, set_hostname, prepare_server
from fab_deploy.utils import detect_os, run_as
from fab_deploy.user import provider_as_ec2, ssh_local_keygen
from fab_deploy import vcs
from fab_deploy.virtualenv import pip_install, virtualenv_create, virtualenv

def go(stage="development", keyname='ec2.development'):
	""" 
	A convenience method to prepare AWS servers.
	
	Use this to create keys, authorize ports, and deploy nodes.
	DO NOT use this step if you've already created keys and opened
	ports on your ec2 instance.
	"""

	# Setup keys and authorize ports
	provider = fabric.api.env.conf['PROVIDER']
	keyname = '%s.%s' % (provider,keyname)
	if 'ec2' in provider:
		ec2_create_key(keyname)
		ec2_authorize_port('default','tcp','22')
		ec2_authorize_port('default','tcp','80')

		# Deploy the nodes for the given stage
		deploy_nodes(stage,keyname)
	elif 'rackspace' == provider:
		deploy_nodes(stage)

	fabric.api.warn(fabric.colors.yellow('Wait 60 seconds for nodes to deploy'))
	time.sleep(60)
	update_nodes()

def go_setup(stage="development"):
	"""
	Install the correct services on each machine
	
    $ fab -i deploy/[your private SSH key here] set_hosts go_setup
	"""
	stage_exists(stage)
	PROVIDER = get_provider_dict()

	# Determine if a master/slave relationship exists for databases in config
	slave = []
	for db in ['mysql','postgresql','postgresql-client']:
		slave.append(any(['slave' in PROVIDER['machines'][stage][name].get('services',{}).get(db,{}) for name in PROVIDER['machines'][stage]]))
	replication = any(slave)
	
	# Begin installing and setting up services
	for name in PROVIDER['machines'][stage]:
		node_dict = PROVIDER['machines'][stage][name]
		host = node_dict['public_ip'][0]
		if host == fabric.api.env.host:
			set_hostname(name)
			prepare_server()
			for service in node_dict['services'].keys():
				settings = node_dict['services'][service]
				if service == 'nginx':
					nginx_install()
					nginx_setup(stage=stage)
				elif service == 'redis':
					redis_install()
					redis_setup()
				elif service == 'uwsgi':
					uwsgi_install()
					uwsgi_setup(stage=stage)
				elif service == 'mysql':
					mysql_install()
					mysql_setup(stage=stage,replication=replication,**settings)
				elif service == 'postgresql':
					postgresql_install(name, node_dict, stage=stage, **settings)
					postgresql_setup(name, node_dict, stage=stage, **settings)
				elif service == 'postgresql-client':
					postgresql_client_install()
				elif service in ['apache']:
					fabric.api.warn(fabric.colors.yellow("%s is not yet available" % service))
				else:
					fabric.api.warn('%s is not an available service' % service)

def go_deploy(stage="development", tagname="trunk"):
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
			# If any of these services are listed then deploy the project
			if list(set(['nginx','uwsgi','apache']) & set(node_dict['services'])):
				deploy_full(tagname,force=True)
	
				# Link the hostname to the <stage>.py file
				# Commented out as the environment-specific settings are called
				# settings/staging.py or settings/production.py, and if someone
				# really needs host-specific settings (e.g. two different files
				# for web1 and web2), then he would write them by hand anyway
				# hostname = get_hostname()
				# host_dir = os.path.join(fabric.api.env.conf['SRC_DIR'],tagname,'project/settings')
				# if not fabric.contrib.files.exists(os.path.join(host_dir,'%s.py' % hostname)):
				# 	link(os.path.join(host_dir,'%s.py' % stage), 
				# 		dest=os.path.join(host_dir,'%s.py' % hostname),
				# 		do_unlink=True, silent=True)
				
def deploy_full(tagname, force=False):
	""" 
	Deploys a project with a given tag name, and then makes
	that deployment the active deployment on the server.
	"""
	deploy_project(tagname,force=force)
	make_active(tagname)

def deploy_project(tagname, force=False):
	""" Deploys project on prepared server. """
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
			vcs.export(tagname, local=True)
		fabric.contrib.project.rsync_project(
			local_dir = os.path.join('/tmp', tagname),
			remote_dir = fabric.api.env.conf['SRC_DIR'],
			exclude = fabric.api.env.conf['RSYNC_EXCLUDE'],
			extra_opts='--links --perms')
		fabric.api.local('rm -rf %s' % os.path.join('/tmp', tagname))

	virtualenv_create(dir=tag_dir)
	pip_install(dir=tag_dir)
	
	fabric.api.sudo('chown -R ubuntu:ubuntu /srv')

def make_src_dir():
	""" Makes the /srv/<project>/ directory and creates the correct permissions """
	fabric.api.sudo('mkdir -p %s' % (fabric.api.env.conf['SRC_DIR']))
	fabric.api.sudo('chown -R ubuntu:ubuntu /srv')

def make_active(tagname):
	""" Make a tag at /srv/<project>/<tagname>  active """
	link(os.path.join(fabric.api.env.conf['SRC_DIR'], tagname),
			'/srv/active', do_unlink=True, silent=True)

def check_active():
	""" Abort if there is no active deployment """
	if not link_exists('/srv/active/'):
		fabric.api.abort(fabric.colors.red('There is no active deployment'))

def undeploy():
	""" Shuts site down. This command doesn't clean everything, e.g.
	user data (database, backups) is preserved. """

	if not fabric.contrib.console.confirm("Do you wish to undeploy host %s?" % fabric.api.env.hosts[0], default=False):
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

