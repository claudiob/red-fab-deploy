import os.path

import fabric.api

def ssh_copy_key(pub_key_file):
	"""
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys for user can be copied at any time::

		fab ssh_copy_key:"/home/kmike/coworker-keys/ivan.id_dsa.pub"
	"""
	
	username = fabric.api.env.conf['USER']
	if not fabric.contrib.console.confirm('Do you wish to copy the ssh key for %s?' % username,default=True):
		username = fabric.api.prompt('Enter the username you wish to use:')
	
	with fabric.api.cd('/home/%s' % username):
		ssh_add_key(pub_key_file)
		fabric.api.sudo('chown -R %s:%s .ssh' % (username, username))

def ssh_add_key(pub_key_file):
	""" 
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys for other developers can be added at any time::

		fab ssh_add_key:"/home/kmike/coworker-keys/ivan.id_dsa.pub"
	"""
	with open(os.path.normpath(pub_key_file), 'rt') as f:
		ssh_key = f.read()
	
	fabric.api.run('mkdir -p .ssh')
	fabric.contrib.files.append('.ssh/authorized_keys', ssh_key)

