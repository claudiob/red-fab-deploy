
#--- Media
def media_rsync():
	"""
	Syncs media from web1 to load1 and web2.
	"""
	if env.host_string in [env.LOAD1, env.WEB2, env.DEV]:
		run('''rsync --recursive %(WEB1)s:%(dest)s/media/uploads/
		%(dest)s/media/uploads/ --size-only''' % env)
	else:
		print('No media to rsync for %(host_string)s' % env)

def media_chown():
	"""
	Changes the ownership of media to www-data:www-data.
	"""
	if env.host_string in [env.LOAD1, env.WEB1, env.WEB2, env.DEV]:
		run('chown -R www-data:www-data %(dest)s/media/uploads' % env)
	else:
		print('No media to chown for %(host_string)s' % env)

def media_chmod():
	"""
	Changes the ownership of media to www-data:www-data.
	"""
	if env.host_string in [env.LOAD1, env.WEB1, env.WEB2, env.DEV]:
		run('chmod -R 755 %(dest)s/media/uploads' % env)
	else:
		print('No media to chown for %(host_string)s' % env)

def media_sync():
	"""
	rsync the media and change ownership
	"""
	media_rsync()
	media_chown()
	media_chmod()

