import fabric.api
import fabric.colors
import fabric.contrib
import os

def link_exists(source):
	""" Determine if a file is a symlink """
	with fabric.api.settings(fabric.api.hide('warnings','stderr','stdout','running'),warn_only=True):
		return fabric.api.run("test -L '%s' && echo OK ; true" % source) == "OK"

def link(source,dest="",use_sudo=False,do_unlink=False,silent=False):
	""" Make a symlink """
	if do_unlink:
		if dest:
			unlink(dest, use_sudo=use_sudo,silent=silent)
		else:
			unlink(os.path.basename(source), use_sudo=use_sudo,silent=silent)
			
	if use_sudo:
		fabric.api.sudo('ln -s %s %s' % (source,dest))
	else:
		fabric.api.run('ln -s %s %s' % (source,dest))

def unlink(source, use_sudo=False,silent=False):
	""" Unlink a symlink """
	if link_exists(source):
		if use_sudo:
			fabric.api.sudo('unlink %s' % source)
		else:
			fabric.api.run('unlink %s' % source)
	elif fabric.contrib.files.exists(source):
		if not silent:
			fabric.api.warn(fabric.colors.yellow("%s already exists" % source))
			return
	else:
		if not silent:
			fabric.api.warn(fabric.colors.yellow("%s does not exist" % source))
			return

def readlink(source):
	""" Read a symlink """
	if fabric.contrib.files.exists(source):
		fabric.api.run('readlink %s' % source)

def file_read(location):
	""" Reads the *remote* file at the given lcoation."""
	return fabric.api.run("cat '%s'" % location)

def file_attribs(location, mode=None, owner=None, group=None, recursive=False, local=False):
	"""Updates the mode/owner/group for the remote file at the given location."""
	recursive = recursive and "-R " or ""
	if local:
		if mode:  fabric.api.local("chmod %s %s '%s'" % (recursive, mode,  location))
		if owner: fabric.api.local("chown %s %s '%s'" % (recursive, owner, location))
		if group: fabric.api.local("chgrp %s %s '%s'" % (recursive, group, location))
	else:
		if mode:  fabric.api.run("chmod %s %s '%s'" % (recursive, mode,  location))
		if owner: fabric.api.run("chown %s %s '%s'" % (recursive, owner, location))
		if group: fabric.api.run("chgrp %s %s '%s'" % (recursive, group, location))

