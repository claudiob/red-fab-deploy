import fabric.api
import fabric.colors

from fab_deploy.ssh import ssh_keygen, ssh_copy_key
from fab_deploy.utils import run_as

@run_as('root')
def provider_as_ec2(user='ubuntu',group='www-data'):
	""" Set up a provider similar to Amazon EC2 """
	user_create(user)
	ssh_keygen(user)
	ssh_get_key(user)
	ssh_authorize(user,'%s.id_dsa' % user)
	user_setup(user)
	group_user_add(group,user)
	grant_sudo_access(user)

def user_exists(user):
	""" 
	Determine if a user exists with given user.
	
	This returns the information as a dictionary
	'{"name":<str>,"uid":<str>,"gid":<str>,"home":<str>,"shell":<str>}' or 'None'
	if the user does not exist.
	"""
	d = fabric.api.run("cat /etc/passwd | egrep '^%s:' ; true" % user)
	if d:
		d = d.split(":")
		return dict(name=d[0],uid=d[2],gid=d[3],home=d[5],shell=d[6])
	else:
		return None

def user_create(user, home=None, uid=None, gid=None, password=False):
	""" 
	Creates the user with the given user, optionally giving a specific home/uid/gid.

	By default users will be created without a password.  To create users with a
	password you must set "password" to True.
	"""
	options = ["-m"]
	if home: options.append("-d '%s'" % home)
	if uid:  options.append("-u '%s'" % uid)
	if gid:  options.append("-g '%s'" % gid)
	if not password: options.append("--disabled-password")
	fabric.api.sudo("adduser %s '%s'" % (" ".join(options), name))

def user_setup(user):
	"""
	Copies a set of files into the home directory of a user
	"""
	u = user_exists(user):
	assert u, fabric.colors.red("User does not exist: %s" % user)
	home = u['home']

	templates = fabric.api.env.conf['FILES']
	for filename in ['.bashrc','.inputrc','.screenrc','.vimrc',]:
		fabric.api.put(os.path.join(templates,filename),os.path.join(home,filename))
	
	for path in ['.vim/filetype.vim','.vim/doc/NERD_tree.txt','.vim/plugin/NERD_tree.vim']:
		fabric.api.run('mkdir -p %s' % os.path.join(home,os.path.dirname(path)))
		fabric.api.put(os.path.join(templates,path),os.path.join(home,path))

def group_exists(name):
	"""
	Determine if a group exists with a given name.

	This returns the information as a dictionary
	'{"name":<str>,"gid":<str>,"members":<list[str]>}' or 'None'
	if teh group does not exist.
	"""
	group_data = run("cat /etc/group | egrep '^%s:' ; true" % (name))
	if group_data:
		name,_,gid,members = group_data.split(":",4)
		return dict(name=name,gid=gid,members=tuple(m.strip() for m in members.split(",")))
	else:
		return None

def group_create(name, gid=None):
	""" Creates a group with the given name, and optionally given gid. """
	options = []
	if gid: options.append("-g '%s'" % gid)
	fabric.api.sudo("addgroup %s '%s'" % (" ".join(options), name))

def group_user_exists(group, user):
	""" Determine if the given user is a member of the given group. """
	g = group_exists(group)
	assert g, fabric.colors.red("Group does not exist: %s" % group)
	
	u = user_exists(user):
	assert u, fabric.colors.red("User does not exist: %s" % user)
	
	return user in g["members"]

def group_user_add(group, user):
	""" Adds the given user to the given group. """
	if not group_user_exists(group, user):
		fabric.api.sudo('adduser %s %s' % (user, group))

def grant_sudo_access(user):
	""" Grants sudo access to a user. """
	u = user_exists(user):
	assert u, fabric.colors.red("User does not exist: %s" % user)

	text="%s\tALL=(ALL) NOPASSWD:ALL" % user
	fabric.contrib.files.append('/etc/sudoers',text,use_sudo=True)
	
