from functools import wraps
import os
import pprint
import re

from fabric.api import *
from fabric.contrib.files import upload_template
from fabric.network import normalize, join_host_strings
from fabric.state import _AttributeDict

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
	if 'conf' in env and 'OS' in env.conf:
		return env.conf['OS']
	output = run('python -c "import platform; print platform.linux_distribution()"')
	name = _codename(*eval(output))
	puts('%s detected' % name)
	return name

def run_as(user):
	"""
	Decorator.  Runs fabric command as specified user.  It is most useful to run
	commands that require root access to server::

		from fabric.api import run
		from fab_deploy.utils import run_as

		@run_as('root')
		def aptitude_update():
			run('aptitude update')
	
	"""
	def decorator(func):
		@wraps(func)
		def inner(*args, **kwargs):
			old_user, host, port = normalize(env.host_string)
			env.host_string = join_host_strings(user, host, port)
			result = func(*args, **kwargs)
			env.host_string = join_host_strings(old_user, host, port)
			return result
		return inner
	return decorator

#def upload_config_template(name, to=None):
#	if to is None:
#		base_dir = env.conf['ENV_DIR'] + "/etc/"
#		run('mkdir -p ' + base_dir)
#		to = base_dir + name
#	upload_template('./config_templates/' + name, to, env.conf, True)

def update_env():
	"""
	Updates :attr:`env.conf` configuration with some defaults and converts
	it to _AttributeDict (that's a dictionary subclass enabling attribute
	lookup/assignment of keys/values).

	Call :func:`update_env` at the end of each server-configuring function.

	::

		from fab_deploy import update_env

		def my_site():
			env.hosts = ['my_site@example.com']
			env.conf = dict(
				DB_PASSWORD = 'password',
			)
			update_env()
	"""
	print env.hosts
	assert len(env.hosts)>0, "Must supply hosts in env.hosts."
	assert len(env.hosts)==1, "Multiple hosts in env.hosts are not supported now. (%s)" % env.hosts
	user, host, port = normalize(env.hosts[0])

	env.conf = getattr(env, 'conf', {})

	if user != 'root':
		HOME_DIR = '/home/%s' % user
	else:
		HOME_DIR = '/root'

	if 'INSTANCE_NAME' not in env.conf:
		env.conf['INSTANCE_NAME'] = user

	defaults = _AttributeDict(
		HG_BRANCH    = 'default',
		SVN_BRANCH   = 'trunk',
		DB           = 'mysql', # Choose from 'mysql' or 'postgresql'
		DB_NAME      = env.conf['INSTANCE_NAME'],
		DB_USER      = 'root',
		DB_PASSWORD  = 'password',
		PROCESSES    = 1,
		SERVER_ADMIN = 'example@example.com',
		SERVER_NAME  = host,
		SERVER_TYPE  = 'nginx', # Choose from 'apache' or 'nginx'
		THREADS      = 15,
		VCS          = 'svn',
		VCS_TAGS     = 'branches',#'tags',

		# these options shouldn't be set by user
		HOME_DIR = HOME_DIR,
		#ENV_DIR  = '/srv/' + env.conf['INSTANCE_NAME'],
		SRC_DIR  = '/srv/' + env.conf['INSTANCE_NAME'],
		USER     = user,
	)
	defaults.update(env.conf)
	env.conf = defaults

	for vcs in ['hg','svn','none']: # expand VCS name to full import path
		if env.conf.VCS == vcs:
			env.conf.VCS = 'fab_deploy.vcs.'+vcs
	
	for db in ['mysql','postgresql']: # expand DB name to full import path
		if env.conf.DB == db:
			env.conf.DB = 'fab_deploy.db.'+db

def delete_pyc():
	""" Deletes *.pyc files from project source dir """
	run("find . -name '*.pyc' -delete")

def print_env():
	""" Prints env values. Useful for debuggins. """
	puts(pprint.pformat(env))

def _data_path(fname):
    """Return the path to a data file of ours."""
    return os.path.join(os.path.split(__file__)[0], fname)

