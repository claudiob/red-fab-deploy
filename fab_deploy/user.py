import fabric.api
import fabric.colors

from fab_deploy.ssh import ssh_copy_key
from fab_deploy.utils import run_as

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
	username = fabric.api.env.conf['USER']
	if not fabric.contrib.console.confirm('Do you wish to create a linux account for %s?' % username,default=True):
		username = fabric.api.prompt('Enter the username you wish to use:')
	
	if _user_exists(username):
		fabric.api.warn(fabric.colors.yellow('The user %s already exists' % username))
		return

	with fabric.api.settings(warn_only=True):
		fabric.api.sudo('adduser --disabled-password %s' % username)
		ssh_copy_key(pub_key_file)

def linux_account_setup():
	"""
	Copies a set of files into the home directory of a user
	"""
	username = fabric.api.env.conf['USER']
	if not fabric.contrib.console.confirm('Do you wish to setup the linux account for %s?' % username,default=True):
		username = fabric.api.prompt('Enter the username you wish to use:')
	
	if not _user_exists(username):
		fabric.api.warn(fabric.colors.yellow('The user %s does not exist' % username))
		return

	user_home = fabric.api.env.conf['HOME_DIR']
	templates = fabric.api.env.conf['FILES']
	for filename in ['.bashrc','.inputrc','.screenrc','.vimrc',]:
		put(os.path.join(templates,filename),os.path.join(user_home,filename))
	
	for path in ['.vim/filetype.vim','.vim/doc/NERD_tree.txt','.vim/plugin/NERD_tree.vim']:
		fabric.api.run('mkdir -p %s' % os.path.join(user_home,os.path.dirname(path)))
		fabric.api.put(os.path.join(templates,path),os.path.join(user_home,path))

def linux_account_addgroup():
	""" Adds a linux account to a group """
	username = fabric.api.env.conf['USER']
	if not fabric.contrib.console.confirm('Do you wish to add a linux group account for %s?' % username,default=True):
		username = fabric.api.prompt('Enter the username you wish to use:')
	
	if not _user_exists(username):
		fabric.api.warn(fabric.colors.yellow('The user %s does not exist' % username))
		return

	group = fabric.api.prompt('Enter the group name you want to add the user to:')
	with fabric.api.settings(warn_only=True):
		fabric.api.sudo('adduser %s %s' % (username,group))

def grant_sudo_access():
	"""
	Grants sudo access to a user
	"""
	username = fabric.api.env.conf['USER']
	if not fabric.contrib.console.confirm('Do you wish to sudo access for %s?' % username,default=True):
		username = fabric.api.prompt('Enter the username you wish to use:')
	
	if not _user_exists(username):
		fabric.api.warn(fabric.colors.yellow('The user %s does not exist' % username))
		return

	text="%s\tALL=(ALL) NOPASSWD:ALL" % username
	fabric.contrib.files.append('/etc/sudoers',text,use_sudo=True)
	
