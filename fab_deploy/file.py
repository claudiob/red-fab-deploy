import fabric.api

def is_link(source):
	""" Determine if a file is a symlink """
	if fabric.contrib.files.exists(source):
		with fabric.api.settings(fabric.api.hide('warnings','stderr','stdout'),warn_only=True):
			output = fabric.api.run('readlink %s' % source)
			return output.succeeded
	else:
		return False

def link(source,dest="",use_sudo=False,do_unlink=False):
	""" Make a symlink """
	if do_unlink:
		if dest:
			unlink(dest, use_sudo=use_sudo)
		else:
			unlink(source, use_sudo=use_sudo)
			
	if use_sudo:
		fabric.api.sudo('ln -s %s %s' % (source,dest))
	else:
		fabric.api.run('ln -s %s %s' % (source,dest))

def unlink(source, use_sudo=False):
	""" Unlink a symlink """
	if is_link(source):
		if use_sudo:
			fabric.api.sudo('unlink %s' % source)
		else:
			fabric.api.run('unlink %s' % source)
	else:
		fabric.api.warn(fabric.colors.yellow("%s already exists" % dest))
		return

def readlink(source):
	""" Read a symlink """
	if fabric.contrib.files.exists(source):
		fabric.api.run('readlink %s' % source)

