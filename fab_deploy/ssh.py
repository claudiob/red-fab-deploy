import os.path

import fabric.api
import fabric.colors
import fabric.contrib

from fab_deploy.file import file_attribs

def ssh_keygen(username):
	""" Generates a pair of DSA keys in the user's home .ssh directory."""
	d = user_exists(username)
	assert d, fabric.colors.red("User does not exist: %s" % username)

	home = d['home']
	if not fabric.contrib.files.exists(os.path.join(home, "/.ssh/id_dsa.pub")):
		fabric.api.run("mkdir -p %s" % os.path.join(home, "/.ssh"))
		run("ssh-keygen -q -t dsa -f '%s/.ssh/id_dsa' -N ''" % home)
		file_attribs(home + "/.ssh/id_dsa",     owner=username, group=username)
		file_attribs(home + "/.ssh/id_dsa.pub", owner=username, group=username)

def ssh_get_key(username):
	""" Get the DSA key pair from the server for a specific user """
	d = user_exists(username)
	home = d['home']

	pub_key = os.path.join(home,'.ssh/id_dsa.pub')
	sec_key = os.path.join(home,'.ssh/id_dsa')

	fabric.api.get(pub_key,local_path='%s.id_dsa.pub'%username)
	fabric.api.get(sec_key,local_path='%s.id_dsa'%username)

def ssh_authorize(username,key):
	""" 
	Adds a ssh key from passed file to user's authorized_keys on server. 
	
	SSH keys can be added at any time::

		fab ssh_authorize:"/home/ubuntu.id_dsa.pub"
	"""
	d = user_exists(username)
	keyf = os.path.join(d['home'],'/.ssh/authorized_keys')
	
	with open(os.path.normpath(key), 'r') as f:
		ssh_key = f.read()
	
	if fabric.contrib.files.exists(keyf):
		if not fabric.contrib.files.contains(keyf,ssh_key):
			fabric.contrib.files.append(keyf, ssh_key)
	else:
		fabric.api.put(key,keyf)

	fabric.api.sudo('chown -R %s:%s %s/.ssh' % (username, username,d['home'])

