import os.path

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import append, exists
from fabric.utils import puts

from fab_deploy.package import *
from fab_deploy.utils import detect_os, run_as

def set_host_name(hostname):
	""" Set the host name on a server """
	#sudo
	pass

def make_src_dir():
	""" Makes the /srv/<project>/ directory and creates the correct permissions """
	sudo('mkdir -p %s' % (env.conf['SRC_DIR']))
	sudo('chown -R www-data:www-data /srv')
	sudo('chmod -R g+w /srv')

def make_active(tagname):
	""" Make a tag at /srv/<project>/<tagname>  active """
	with cd('/srv'):
		run('ln -s %s/%s active' % (env.conf['SRC_DIR'],tagname))

def prepare_server():
	""" Prepares server: installs system packages. """
	setup_backports()
	install_common_software()

def setup_backports():
	""" Adds backports repo to apt sources. """
	os = detect_os()
	backports = {
		'lenny': 'http://backports.debian.org/debian-backports lenny-backports main contrib non-free',
		'squeeze': 'http://backports.debian.org/debian-backports squeeze-backports main contrib non-free',
	}

	if os not in backports:
		warn(yellow("Backports are not available for %s" % os))
		return

	run("echo 'deb %s' > /etc/apt/sources.list.d/backports.sources.list" % backports[os])
	with settings(warn_only=True):
		package_update()
		package_upgrade()

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
		'memcached',
		'psmisc',
		'python2.6',
		'python2.6-dev',
		'python-imaging',
		'python-pip',
		'python-setuptools',
		'python-software-properties',
		'python-virtualenv',
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
		abort(red('Your OS (%s) is currently unsupported.' % os))
	
	with settings(warn_only=True):
		package_update()
		package_upgrade()

	package_install(common_packages + extra_packages[os])

	vcs_options = {'lenny': '-t lenny-backports'}
	package_install(['mercurial','git-core'], vcs_options.get(os, ""))

def _user_exists(username):
	""" Determine if a user exists """
	with settings(hide('stderr'), warn_only=True):
		output = run('id %s' % username)
	return output.succeeded

@run_as('root')
def rackspace_as_ec2(pub_key_file):
	linux_account_create(pub_key_file)
	linux_account_setup()
	linux_account_addgroup()
	grant_sudo_access()
	
def linux_account_create(pub_key_file):
	"""
	Creates linux account and sets up ssh access. 
	
	If there is no linux account for user specified in :attr:`env.hosts`
	then add a new linux server user, manually or using
	
	::
	
	    fab create_linux_account:"/home/<user>/.ssh/id_rsa.pub"
	
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
	if not confirm('Do you wish to create a linux account for %s?' % username,default=True):
		username = prompt('Enter the username you wish to use:')
	
	if _user_exists(username):
		warn(yellow('The user %s already exists' % username))
		return

	with (settings(warn_only=True)):
		sudo('adduser --disabled-password %s' % username)
		ssh_copy_key(pub_key_file)

def linux_account_setup():
	"""
	Copies a set of files into the home directory of a user
	"""
	username = env.conf['USER']
	if not confirm('Do you wish to setup the linux account for %s?' % username,default=True):
		username = prompt('Enter the username you wish to use:')
	
	if not _user_exists(username):
		warn(yellow('The user %s does not exist' % username))
		return

	user_home = env.conf['HOME_DIR']
	templates = env.conf['FILES']
	for filename in ['.bashrc','.inputrc','.screenrc','.vimrc',]:
		put(os.path.join(templates,filename),os.path.join(user_home,filename))
	
	for path in ['.vim/filetype.vim','.vim/doc/NERD_tree.txt','.vim/plugin/NERD_tree.vim']:
		run('mkdir -p %s' % os.path.join(user_home,os.path.dirname(path)))
		put(os.path.join(templates,path),os.path.join(user_home,path))

def linux_account_addgroup():
	""" Adds a linux account to a group """
	username = env.conf['USER']
	if not confirm('Do you wish to add a linux group account for %s?' % username,default=True):
		username = prompt('Enter the username you wish to use:')
	
	if not _user_exists(username):
		warn(yellow('The user %s does not exist' % username))
		return

	group = prompt('Enter the group name you want to add the user to:')
	with (settings(warn_only=True)):
		sudo('adduser %s %s' % (username,group))

def grant_sudo_access():
	"""
	Grants sudo access to a user
	"""
	username = env.conf['USER']
	if not confirm('Do you wish to sudo access for %s?' % username,default=True):
		username = prompt('Enter the username you wish to use:')
	
	if not _user_exists(username):
		warn(yellow('The user %s does not exist' % username))
		return

	text="%s\tALL=(ALL) NOPASSWD:ALL" % username
	append('/etc/sudoers',text,use_sudo=True)
	
def ssh_copy_key(pub_key_file):
	"""
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys for user can be copied at any time::

		fab ssh_copy_key:"/home/kmike/coworker-keys/ivan.id_dsa.pub"
	"""
	
	username = env.conf['USER']
	if not confirm('Do you wish to copy the ssh key for %s?' % username,default=True):
		username = prompt('Enter the username you wish to use:')
	
	with cd('/home/%s' % username):
		ssh_add_key(pub_key_file)
		sudo('chown -R %s:%s .ssh' % (username, username))

def ssh_add_key(pub_key_file):
	""" 
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys for other developers can be added at any time::

		fab ssh_add_key:"/home/kmike/coworker-keys/ivan.id_dsa.pub"
	"""
	with open(os.path.normpath(pub_key_file), 'rt') as f:
		ssh_key = f.read()
	
	run('mkdir -p .ssh')
	append('.ssh/authorized_keys', ssh_key) # Fabric 1.0
	#append(ssh_key, '.ssh/authorized_keys') # Fabric 0.9.4

