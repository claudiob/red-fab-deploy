from datetime import datetime

import fabric.api, fabric.contrib.files

from fab_deploy.package import package_install, package_add_repository

def _postgresql_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('postgresql --version')
	return output.succeeded

def _postgresql_client_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('psql --version')
	return output.succeeded

def postgresql_install(node_dict, stage, **options):
	""" Installs postgreSQL """

	if _postgresql_is_installed():
		fabric.api.warn(fabric.colors.yellow('PostgreSQL is already installed.'))
		return
	
	config = get_provider_dict()
	if 'slave' in options:
		master = config['machines'][stage][options['slave']]
		options.update(master['services']['postgresql'])
	
	package_add_repository('ppa:pitti/postgresql')
	package_install(['postgresql', 'xfsprogs', 'mdadm'])
	
	# Figure out cluster name
	output = fabric.api.run('pg_lsclusters -h')
	version, cluster = output.split()[:2]
	
	if 'ec2'  in fabric.api.env.conf['PROVIDER']:
		# Create two ebs volumes
		import boto
		ec2 = boto.connect_ec2(fabric.api.env.conf['AWS_ACCESS_KEY_ID'],
							   fabric.api.env.conf['AWS_SECRET_ACCESS_KEY'],
							   region = fabric.api.env.conf['PROVIDER'])
		
		volume1 = ec2.create_volume(options.get('max-size', 10)/2, config['location'])
		volume1.attach(node_dict['id'], '/dev/sdf')
		volume2 = ec2.create_volume(options.get('max-size', 10)/2, config['location'])
		volume2.attach(node_dict['id'], '/dev/sdg')
							   
		# RAID 0 together the EBS volumes, and format the result as xfs.  Mount at /data.
		fabric.api.sudo('mdadm --create /dev/md0 --level=0 --raid-devices=2 /dev/sdf /dev/sdg')
		fabric.api.sudo('mkfs.xfs /dev/md0')
		fabric.api.sudo('mkdir -p /data')
		fabric.api.sudo('chown postgres:postgres /data')
		fabric.api.sudo('chmod 644 /data')
		fabric.api.sudo('echo "/dev/md0  /data  auto  defaults  0  0" >> /etc/fstab')
		fabric.api.sudo('mount /data')

		# Move cluster/dbs to /data		
		fabric.api.sudo('pg_dropcluster --stop %s %s' % (version, cluster))
		fabric.api.sudo('pg_createcluster --start -d /data -e UTF-8 %s %s' % (version, cluster))
	
	else:
		fabric.api.warn(fabric.colors.yellow('PostgreSQL advanced drive setup (RAID 0 + XFS) is not currently supported on non-ec2 instances'))

	# Set up postgres config files - Allow global listening (have a firewall!) and local ubuntu->your user connections
	pg_dir = '/etc/postgresql/%s/%s/' % (version, cluster)
	fabric.contrib.files.comment(pg_dir + 'postgresql.conf', 'listen_addresses', True)
	fabric.contrib.files.append(pg_dir + 'postgresql.conf', "listen_addresses = '*'", True)

	fabric.contrib.files.append(pg_dir + 'pg_hba.conf', "host all all 0.0.0.0/0 md5", True)
	fabric.contrib.files.append(pg_dir + 'pg_ident.conf', "ubuntu ubuntu %s" % options['user'], True)	
	
	
	# Figure out if we're a master
	if 'slave' not in options and any('slave' in values.get('services', {}).get('postgresql', {}) for name, values in config['machines'][stage]):
		# We're a master!
		
		fabric.contrib.files.append(pg_dir + 'postgresql.conf', [
			'wal_level = hot_standby',
			'max_wal_senders = 1',
			'checkpoint_segments = 8',
			'wal_keep_segments = 8'], True)
		
		fabric.contrib.files.append(pg_dir + 'pg_hba.conf', "host replication all 0.0.0.0/0 md5", True)
		
	elif 'slave' in options:
		# We're a slave!
		
		fabric.contrib.files.append(pg_dir + 'postgresql.conf', [
			'hot_standby = on',
			'checkpoint_segments = 8',
			'wal_keep_segments = 8'], True)
		
		fabric.contrib.files.append('/data/recovery.conf', [
			"standby_mode = 'on'",
			"primary_conninfo = 'host=%s port=5432 user=%s password=%s'" % (master, options['user'], options['password']),
			"trigger_file = '/data/failover"], True)
		
	with cd('/srv/active'):
		fabric.api.sudo('''scp -ri %s %s:/data/* /data''' % (env.key_filename, master['private_ip'][0]))
		
	
	fabric.api.sudo('service postgresql restart')
	
def postgresql_client_install():
	if _postgresql_client_is_installed():
		fabric.api.warn(fabric.colors.yellow('The PostgreSQL client is already installed.'))
		return
	
	package_add_repository('ppa:pitti/postgresql')
	package_install(['postgresql-client', 'python-psycopg2'])
	
def postgresql_setup(node_dict, stage, settings):
	sudo('su postgres -c "createuser -s -U postgres -P %s"' % (settings['user']))
	sudo('su postgres -c "createdb -U %s %s"' % (settings['user'], settings['name']))

def postgresql_execute(sql, user='', password=''):
	"""
	Executes passed sql command using postgresql shell.
	"""
	return fabric.api.run("echo '%s' | psql -u%s -p%s" % (sql, user, password))

def postgresql_create_db():
	"""
	Create an empty postgresql database.
	"""
	database = fabric.api.runprompt('Please enter database name:')
	
	fabric.api.run("createdb %s" % (database))

def postgresql_create_user():
	"""
	Creates a new postgresql user.
	"""
	user     = fabric.api.runprompt('Please enter username:')
	new_user = fabric.api.runprompt('Please enter new username:')
	
	fabric.api.run("createuser %s -P -U %s" % (new_user, user))

def postgresql_drop_user():
	""" Drop a postgresql user """
	pass

def postgresql_dump():
	""" Runs postgresqldump. Result is stored at /srv/active/sql/ """
	dir = '/srv/active/sql/'
	pass

def postgresql_load():
	""" Load a postgresql database """
	pass

def postgresql_backup():
	""" Backup the database """
	pass

