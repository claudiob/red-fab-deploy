from functools import wraps
import json
import os
import pprint
import re

import fabric.api
import fabric.colors

def _codename(distname, version, id):
	patterns = [
		('lenny',    ('debian', '^5', '')),
		('squeeze',  ('debian', '^6', '')),
		('lucid',    ('Ubuntu', '^10.04', '')),
		('maverick', ('Ubuntu', '^10.10', '')),
	]
	for name, p in patterns:
		if re.match(p[0], distname) and re.match(p[1], version) and re.match(p[2], id):
			return name

def detect_os():
	if 'conf' in fabric.api.env and 'OS' in fabric.api.env.conf:
		return fabric.api.env.conf['OS']
	output = fabric.api.run('python -c "import platform; print platform.linux_distribution()"')
	name = _codename(*eval(output))
	fabric.api.puts('%s detected' % name)
	return name

def run_as(user):
	"""
	Decorator.  Runs fabric command as specified user.  It is most useful to run
	commands that require root access to server::

		from fabric.api import run
		from fab_deploy.utils import run_as

		@run_as('root')
		def package_update():
			fabric.api.run('package update')
	
	"""
	def decorator(func):
		@wraps(func)
		def inner(*args, **kwargs):
			old_user, host, port = fabric.network.normalize(fabric.api.env.host_string)
			fabric.api.env.host_string = fabric.network.join_host_strings(user, host, port)
			result = func(*args, **kwargs)
			fabric.api.env.host_string = fabric.network.join_host_strings(old_user, host, port)
			return result
		return inner
	return decorator

def update_env():
	"""
	Updates :attr:`env.conf` configuration with some defaults and converts
	it to _AttributeDict (that's a dictionary subclass enabling attribute
	lookup/assignment of keys/values).

	Call :func:`update_env` at the end of each server-configuring function.

	::

		from fab_deploy import update_env

		def my_site():
			fabric.api.env.hosts = ['my_site@example.com']
			fabric.api.env.conf = dict(
				INSTANCE_NAME = 'projectname',
				PROVIDER = 'ec2_us_east',
				REPO = 'http://some.repo.com/projectname/',
			)
			update_env()
	"""
	
	fabric.api.env.conf = getattr(fabric.api.env, 'conf', {})
	
	defaults = fabric.state._AttributeDict(
		DB            = 'mysql',       # Choose from 'mysql' or 'postgresql'
		DB_PASSWD     = 'password',    # DB root user password, please replace
		INSTANCE_NAME = 'projectname', # This should be the project name
		PROVIDER      = 'ec2_us_east', # use 'rackspace','ec2_us_east', or 'ec2_us_west'
		SERVER_TYPE   = 'nginx',       # Choose from 'apache' or 'nginx'
		VCS           = 'svn',         # Currently only svn works
		VCS_TAGS      = 'tags',        # Could be 'tags' or 'branches' in svn

		# these options shouldn't be set by user
		ENV_DIR  = '/srv/active/env/',
		SRC_DIR  = os.path.join('/srv', fabric.api.env.conf['INSTANCE_NAME']),
		FILES    = os.path.join(os.path.dirname(__file__),'templates'),
	)
	defaults.update(fabric.api.env.conf)
	fabric.api.env.conf = defaults

	# expand VCS name to full import path
	for vcs in ['svn','tar']: 
		if fabric.api.env.conf.VCS == vcs:
			fabric.api.env.conf.VCS = 'fab_deploy.vcs.%s' % vcs
			break

def set_hosts(stage='development',username='ubuntu',machine=''):
	"""
	The stage specifies which group of machines to set the hosts for

	The username specifies which user to use when setting the hosts

	The machine is optional and can specify a specific machine within
	a stage to set the host for.
	"""
	hosts = []
	PROVIDER = json.loads(open('fabric.conf','r').read()) 
	if stage in PROVIDER['machines']:
		for name in PROVIDER['machines'][stage]:
			if (machine and machine == name) or not machine:
				node_dict = PROVIDER['machines'][stage][name]
				if 'public_ip' in node_dict:
					public_ip = node_dict['public_ip']
					for ip in public_ip:            
						hosts.append('%s@%s' % (username,ip))  
				else:
					fabric.api.warn(fabric.colors.yellow('No public IPs found for %s in %s' % (name,stage)))
			#else:
			#	fabric.api.warn(fabric.colors.yellow('No machines found matching %s in %s' % (machine,stage)))
	fabric.api.env.hosts = hosts
	update_env()
	
def delete_pyc():
	""" Deletes *.pyc files from project source dir """
	fabric.api.run("find . -name '*.pyc' -delete")

def debug_env():
	""" Prints env values. Useful for debugging. """
	fabric.api.puts(pprint.pformat(fabric.api.env))

