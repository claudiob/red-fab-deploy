import os.path

from fabric.api import *
from fabric.contrib.files import append, exists
from fabric.utils import puts, abort

from fab_deploy.utils import run_as, detect_os

def prepare_server():
	""" Prepares server: installs system packages. """
	setup_backports()
	install_common_software()

@run_as('root')
def setup_backports():
	""" Adds backports repo to apt sources. """
	os = detect_os()
	backports = {
		'lenny': 'http://backports.debian.org/debian-backports lenny-backports main contrib non-free',
		'squeeze': 'http://backports.debian.org/debian-backports squeeze-backports main contrib non-free',
	}

	if os not in backports:
		puts("Backpors are not available for %s" % os)
		return

	run("echo 'deb %s' > /etc/apt/sources.list.d/backports.sources.list" % backports[os])
	with settings(warn_only=True):
		aptitude_update()

@run_as('root')
def install_common_software():
	""" Installs common system packages. """
	common_packages = [
		'ack-grep',
		'build-essential',
		'curl',
		'gcc',
		'libcurl3-dev',
		'libjpeg-dev',
		'libssl-dev',
		'locales-all',
		'memcached',
		'psmisc',
		'python2.6',
		'python-imaging',
		'python-pip',
		'python-profiler',
		'python-setuptools',
		'python-software-properties',
		'python2.6-dev',
		'rsync',
		'screen',
		'subversion',
		'zlib1g-dev',
	]
	extra_packages = {
		'lenny': [],
		'sqeeze': [],
		'lucid': [],
		'maverick': [],
	}

	os = detect_os()
	if os not in extra_packages:
		abord('Your OS (%s) is currently unsupported.' % os)
	
	aptitude_install(" ".join(common_packages + extra_packages[os]))

	vcs_options = {'lenny': '-t lenny-backports'}
	aptitude_install('mercurial git-core', vcs_options.get(os, ""))
	#aptitude_install('bzr', '--without-recommends')

	run('easy_install -U pip')
	run('pip install -U virtualenv')

def _user_exists(username):
	""" Determine if a user exists """
	with settings(hide('stderr'), warn_only=True):
		output = run('id %s' % username)
	return output.succeeded

@run_as('root')
def create_linux_account(pub_key_file):
	"""
	Creates linux account and setups ssh access. 
	
	If there is no linux account for user specified in :attr:`env.hosts`
	then add a new linux server user, manually or using
	
	::
	
	    fab create_linux_account:"/home/kmike/.ssh/id_rsa.pub"
	
	You'll need the ssh public key.

	:func:`create_linux_account<fab_deploy.system.create_linux_account>`
	creates a new linux user and uploads provided ssh key. Test that ssh
	login is working::
	
	    ssh my_site@example.com
	
	.. note::
	
	    Fabric commands should be executed in shell from the project root
	    on local machine (not from the python console, not on server shell).
	"""
	username = env.conf['USER']
	if _user_exists(username):
		warn('The user %s already exists' % username)
		return

	with (settings(warn_only=True)):
		#run('adduser %s --disabled-password --gecos ""' % username)
		run('adduser %s --disabled-password' % username)
		ssh_copy_key(pub_key_file)

@run_as('root')
def ssh_copy_key(pub_key_file):
	"""
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys for user can be copied at any time::

		fab ssh_copy_key:"/home/kmike/coworker-keys/ivan.id_dsa.pub"
	"""
	
	username = env.conf['USER']
	with open(os.path.normpath(pub_key_file), 'rt') as f:
		ssh_key = f.read()
	
	with cd('/home/' + username):
		run('mkdir -p .ssh')
		append('.ssh/authorized_keys', ssh_key) # Fabric 1.0
		#append(ssh_key, '.ssh/authorized_keys') # Fabric 0.9.4
		run('chown -R %s:%s .ssh' % (username, username))

def ssh_add_key(pub_key_file):
	""" 
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys for other developers can be added at any time::

		fab ssh_add_key:"/home/kmike/coworker-keys/ivan.id_dsa.pub"
	"""
	with open(os.path.normpath(pub_key_file), 'rt') as f:
		ssh_key = f.read()
	run('mkdir -p .ssh')
	append('.ssh/authorized_keys', ssh_key)

@run_as('root')
def aptitude_install(packages, options=''):
	""" Installs package via aptitude. """
	run('aptitude install %s -y %s' % (options, packages,))

@run_as('root')
def aptitude_update():
	""" Update aptitude packages on the server """
	run('aptitude update')
	
