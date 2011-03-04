import fabric.api

def media_rsync():
	"""
	Syncs media in /srv/active/uploads/ directory from given host
	"""
	media_user = prompt('Please enter the media host user:')
	media_host = prompt('Please enter the media host IP:')
	fabric.api.run('''rsync --recursive %s@%s:/srv/active/uploads/ /srv/active/uploads/ --size-only''' % (media_user,media_host))

def media_chown():
	"""
	Changes the ownership of media to www-data:www-data.
	"""
	fabric.api.sudo('chown -R www-data:www-data /srv/active/uploads')

def media_chmod():
	"""
	Changes the ownership of media to www-data:www-data.
	"""
	fabric.api.sudo('chmod -R 755 /srv/active/uploads')

def media_sync():
	"""
	rsync the media and change ownership
	"""
	media_rsync()
	media_chown()
	media_chmod()

