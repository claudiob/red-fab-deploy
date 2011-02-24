import os.path

from fabric.api import *
from fabric.contrib.files import append
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

@run_as('root')
def create_linux_account(pub_key_file):
	""" Creates linux account and setups ssh access. """
	with open(os.path.normpath(pub_key_file), 'rt') as f:
		ssh_key = f.read()
	username = env.conf['USER']
	with (settings(warn_only=True)):
		run('adduser %s --disabled-password --gecos ""' % username)
		with cd('/home/' + username):
			run('mkdir -p .ssh')
			append('.ssh/authorized_keys', ssh_key)
			run('chown -R %s:%s .ssh' % (username, username))

def ssh_add_key(pub_key_file):
	""" Adds a ssh key from passed file to user's authorized_keys on server. """
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
	
