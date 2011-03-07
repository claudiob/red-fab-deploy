from functools import wraps
import os
import pprint
import re

import fabric.api

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
				INSTANCE_NAME = 'my_site',
			)
			update_env()
	"""
	
	assert len(fabric.api.env.hosts)>0,  fabric.colors.red("Must supply hosts in env.hosts.")
	assert len(fabric.api.env.hosts)==1, fabric.colors.red("Multiple hosts in env.hosts are not supported now. (%s)" % fabric.api.env.hosts)
	user, host, port = fabric.network.normalize(fabric.api.env.hosts[0])

	fabric.api.env.user = user
	fabric.api.env.conf = getattr(fabric.api.env, 'conf', {})
	
	if user != 'root':
		HOME_DIR = '/home/%s' % user
	else:
		HOME_DIR = '/root'

	if 'INSTANCE_NAME' not in fabric.api.env.conf:
		fabric.api.env.conf['INSTANCE_NAME'] = user

	defaults = fabric.state._AttributeDict(
		DB           = 'mysql', # Choose from 'mysql' or 'postgresql'
		PROCESSES    = 1,
		SERVER_ADMIN = 'example@example.com',
		SERVER_NAME  = host,
		SERVER_TYPE  = 'nginx', # Choose from 'apache' or 'nginx'
		SRV_INT      = host,
		THREADS      = 15,
		VCS          = 'svn',
		VCS_TAGS     = 'tags',

		# these options shouldn't be set by user
		HOME_DIR = HOME_DIR,
		ENV_DIR  = '/srv/active/env/',
		SRC_DIR  = '/srv/%s' % fabric.api.env.conf['INSTANCE_NAME'],
		FILES    = os.path.join(os.path.dirname(__file__),'templates'),
		USER     = user,
	)
	defaults.update(fabric.api.env.conf)
	fabric.api.env.conf = defaults

	for db in ['mysql','postgresql']: # expand DB name to full import path
		if fabric.api.env.conf.DB == db:
			fabric.api.env.conf.DB = 'fab_deploy.db.%s' % db
			break

	for server in ['apache','nginx',]: # expand server name to full import path
		if fabric.api.env.conf.SERVER_TYPE == server:
			fabric.api.env.conf.SERVER_TYPE = 'fab_deploy.server.%s' % db
			break

	for vcs in ['svn','tar']: # expand VCS name to full import path
		if fabric.api.env.conf.VCS == vcs:
			fabric.api.env.conf.VCS = 'fab_deploy.vcs.%s' % vcs
			break
	
def delete_pyc():
	""" Deletes *.pyc files from project source dir """
	fabric.api.run("find . -name '*.pyc' -delete")

def debug_env():
	""" Prints env values. Useful for debugging. """
	fabric.api.puts(pprint.pformat(fabric.api.env))

