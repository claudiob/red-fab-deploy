from datetime import datetime
import time

import fabric.api, fabric.contrib.files

from fab_deploy.package import package_install, package_add_repository
from fab_deploy.machine import get_provider_dict
from fab_deploy.utils import append

def _postgresql_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('postgresql --version')
	return output.succeeded

def _postgresql_client_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('psql --version')
	return output.succeeded

def postgresql_install(id, node_dict, stage, **options):
	""" Installs postgreSQL """

	if _postgresql_is_installed():
		fabric.api.warn(fabric.colors.yellow('PostgreSQL is already installed.'))
		return
	
	config = get_provider_dict()
	if 'slave' in options:
		master = config['machines'][stage][options['slave']]
		options.update(master['services']['postgresql'])
	
	package_add_repository('ppa:pitti/postgresql')
	package_install(['postgresql', 'python-psycopg2'])
	
	# Figure out cluster name
	output = fabric.api.run('pg_lsclusters -h')
	version, cluster = output.split()[:2]
	
	if 'ec2' in fabric.api.env.conf['PROVIDER']:
		if not options.get('simple'):
			package_install('xfsprogs')
			package_install('mdadm', '--no-install-recommends')
			
			# Create two ebs volumes
			import boto.ec2
			ec2 = boto.ec2.connect_to_region(config['location'][:-1],
								aws_access_key_id = fabric.api.env.conf['AWS_ACCESS_KEY_ID'],
								aws_secret_access_key = fabric.api.env.conf['AWS_SECRET_ACCESS_KEY'])
			
			tag1 = u'%s-1' % id
			tag2 = u'%s-2' % id
			if not any(vol for vol in ec2.get_all_volumes() if vol.tags.get(u'Name') == tag1):
				volume1 = ec2.create_volume(options.get('max-size', 10)/2, config['location'])
				volume1.add_tag('Name', tag1)
				volume1.attach(node_dict['id'], '/dev/sdf')
			if not any(vol for vol in ec2.get_all_volumes() if vol.tags.get(u'Name') == tag2):
				volume2 = ec2.create_volume(options.get('max-size', 10)/2, config['location'])
				volume2.add_tag('Name', tag2)
				volume2.attach(node_dict['id'], '/dev/sdg')
			
			time.sleep(10)
			
			# RAID 0 together the EBS volumes, and format the result as xfs.  Mount at /data.
			if not fabric.contrib.files.exists('/dev/md0', True):
				fabric.api.sudo('mdadm --create /dev/md0 --level=0 --raid-devices=2 /dev/sdf /dev/sdg')
				fabric.api.sudo('mkfs.xfs /dev/md0')
			
			# Add mountpoint
			if not fabric.contrib.files.exists('/data'):
				fabric.api.sudo('mkdir -p /data')
				fabric.api.sudo('chown postgres:postgres /data')
				fabric.api.sudo('chmod 644 /data')
			
			# Add to fstab and mount
			append('/etc/fstab', '/dev/md0  /data  auto  defaults  0  0', True)
			with fabric.api.settings(warn_only = True):
				fabric.api.sudo('mount /data')
	
			# Move cluster/dbs to /data
			if fabric.api.run('pg_lsclusters -h').split()[5] != '/data':
				fabric.api.sudo('pg_dropcluster --stop %s %s' % (version, cluster))
				fabric.api.sudo('pg_createcluster --start -d /data -e UTF-8 %s %s' % (version, cluster))
	
	else:
		fabric.api.warn(fabric.colors.yellow('PostgreSQL advanced drive setup (RAID 0 + XFS) is not currently supported on non-ec2 instances'))

	fabric.api.sudo('service postgresql stop')

	# Set up postgres config files - Allow global listening (have a firewall!) and local ubuntu->your user connections
	pg_dir = '/etc/postgresql/%s/%s/' % (version, cluster)
	fabric.contrib.files.comment(pg_dir + 'postgresql.conf', 'listen_addresses', True)
	append(pg_dir + 'postgresql.conf', "listen_addresses = '*'", True)

	append(pg_dir + 'pg_hba.conf', "host all all 0.0.0.0/0 md5", True)
	fabric.contrib.files.sed(pg_dir + 'pg_hba.conf', "ident", "trust", use_sudo=True)
	
	# Figure out if we're a master
	if 'slave' not in options and any('slave' in values.get('services', {}).get('postgresql', {})
									  for name, values in config['machines'][stage].iteritems()):
		# We're a master!
		
		append(pg_dir + 'postgresql.conf', [
			'wal_level = hot_standby',
			'max_wal_senders = 1',
			'checkpoint_segments = 8',
			'wal_keep_segments = 8'], True)
		
		append(pg_dir + 'pg_hba.conf', "host replication all 0.0.0.0/0 md5", True)
		
	elif 'slave' in options:
		# We're a slave!
		
		append(pg_dir + 'postgresql.conf', [
			'hot_standby = on',
			'checkpoint_segments = 8',
			'wal_keep_segments = 8'], True)
		
		#fabric.api.sudo('rm -rf /data/*')
		append('/data/recovery.conf', [
			"standby_mode = 'on'",
			"primary_conninfo = 'host=%s port=5432 user=%s password=%s'" % (master['public_ip'][0], options['user'], options['password']),
			"trigger_file = '/data/failover'"], True)
		
		fabric.api.local('''ssh -i %s ubuntu@%s sudo tar czf - /data | ssh -i deploy/nbc-west.pem ubuntu@%s sudo tar xzf - -C /''' % (fabric.api.env.key_filename[0], master['public_ip'][0], node_dict['public_ip'][0]))
		fabric.api.sudo('chown -R postgres:postgres /data')
	
	fabric.api.sudo('service postgresql start')
	
def postgresql_client_install():
	if _postgresql_client_is_installed():
		fabric.api.warn(fabric.colors.yellow('The PostgreSQL client is already installed.'))
		return
	
	package_add_repository('ppa:pitti/postgresql')
	package_install(['postgresql-client', 'python-psycopg2'])
	
	# PGPool
	package_install('libpq-dev')
	'http://pgfoundry.org/frs/download.php/2958/pgpool-II-3.0.3.tar.gz'
	
def postgresql_setup(id, node_dict, stage, **options):
	if 'slave' not in options:
		with fabric.api.settings(warn_only = True):
			fabric.api.sudo('su postgres -c "createuser -s -U postgres -P %s"' % (options['user']))
			fabric.api.sudo('su postgres -c "createdb -U %s %s"' % (options['user'], options['name']))

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

