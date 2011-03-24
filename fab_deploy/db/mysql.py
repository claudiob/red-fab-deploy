from datetime import datetime
import os

import fabric.api

from fab_deploy.machine import get_provider_dict
from fab_deploy.package import package_install
from fab_deploy.system import get_hostname, get_internal_ip, service
from fab_deploy.utils import detect_os

def _mysql_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('mysql --version')
	return output.succeeded
	
def mysql_install():
	""" Installs MySQL """
	if _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL is already installed.'))
		return

	# Ensure mysql won't ask for a password on installation
	# See the following:
	# http://serverfault.com/questions/19367/scripted-install-of-mysql-on-ubuntu
	# http://www.muhuk.com/2010/05/how-to-install-mysql-with-fabric/

	os = detect_os()
	package_install('debconf-utils')
	
	# get the password
	if 'DB_PASSWD' in fabric.api.env.conf:
		passwd = fabric.api.env.conf['DB_PASSWD']
	else:
		passwd = fabric.api.prompt('Please enter MySQL root password:')
	
	# get the correct version for installation
	mysql_versions = {
		'lenny': '5.0',
		'sqeeze': '5.1',
		'lucid': '5.1',
		'maverick': '5.1',
	}
	version = mysql_versions[os]

	debconf_defaults = [
		"mysql-server-%s mysql-server/root_password password %s" % (version,passwd),
		"mysql-server-%s mysql-server/root_password_again password %s" % (version,passwd),
	]

	fabric.api.sudo("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

	fabric.api.warn(fabric.colors.yellow('The password for mysql "root" user will be set to "%s"' % passwd))

	common_packages = [
		'automysqlbackup',
		'sendmail',
		'mysql-server-%s' % version,
		'python-mysqldb',
		]
	extra_packages = {
		'lenny'   : ['libmysqlclient15-dev',],
		'sqeeze'  : ['libmysqlclient-dev',],
		'lucid'   : ['libmysqlclient-dev',],
		'maverick': ['libmysqlclient-dev',],
	}
	package_install(common_packages + extra_packages[os], "--no-install-recommends")

def mysql_setup(**kwargs):
	"""
	Method to set up mysql
	
	This method takes kwargs that can define the stage, the
	name of the database to create, the user and password to enable,
	or the slave database record.  In the case of slave it will look
	up the record from the conf file.
	"""
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	# Get Parameters
	stage          = kwargs.get('stage',None)
	name           = kwargs.get('name',None)
	user           = kwargs.get('user',None)
	password       = kwargs.get('password',None)
	slave          = kwargs.get('slave',None)        # Name of the master database
	slave_user     = kwargs.get('slave_user','slave_user')
	slave_password = kwargs.get('slave_password','password')
	replication    = kwargs.get('replication',False) # Do Master/Slave replication
	
	# The root db password for setup
	root_passwd = ''
	if 'DB_PASSWD' in fabric.api.env.conf:
		root_passwd = fabric.api.env.conf['DB_PASSWD']

	# Private IP is necessary for bind-address
	private_ip = get_internal_ip()
	
	# Update the bind-address to the internal ip
	mysql_conf = '/etc/mysql/my.cnf'
	before = "bind-address[[:space:]]*=[[:space:]]*127.0.0.1"
	after  = "bind-address = %s" % private_ip
	if not fabric.contrib.files.contains(mysql_conf, after):
		fabric.contrib.files.sed(mysql_conf,before,after,
			use_sudo=True, backup='.bkp')
	
	# Create the database user
	if user and password and not slave:
		mysql_create_user(user='root',password=root_passwd,
				new_user=user,new_password=password)

	# Create the database
	if name:
		mysql_create_db(user='root',password=root_passwd, 
				database=name)
	
	# If replication is True then we must do the setup
	if replication:
		PROVIDER = get_provider_dict()
		# If the replication is True and the 'slave' key is given then this should be set up
		# as a slave database and we should do a conf file lookup to return values 
		# for name, user and password to use in setup
		if slave:
			if slave in PROVIDER['machines'][stage]:
				# Get the private IP of the master database
				master_ip = PROVIDER['machines'][stage][slave]['private_ip'][0]

				# Get the settings of the master database
				settings = PROVIDER['machines'][stage][slave]['services']['mysql']
				name     = settings.get('name',None)
				user     = settings.get('user',None)
				password = settings.get('password',None)
	
				# Create the database	
				mysql_create_db(user='root',password=root_passwd, 
					database=name)
				
				# Set up a slave conf file and restart
				context = {
					'db_name'     : name,
					'db_password' : slave_password,
					'db_user'     : slave_user,
					'master_ip'   : master_ip,
				}
				template = os.path.join(fabric.api.env.conf['FILES'],'mysqld_slave.cnf')
				fabric.contrib.files.upload_template(template,'/etc/mysql/conf.d/',
					context=context,use_sudo=True)
				mysql_restart()

				# Load the data from master
				mysql_execute("""LOAD DATA FROM MASTER;""" , 'root', root_passwd)
				mysql_restart()

				log_file = fabric.api.prompt('Enter the master log file name:')
				log_pos  = fabric.api.prompt('Enter the master log position:')

				mysql_execute("""STOP SLAVE;CHANGE MASTER TO MASTER_HOST="%s", MASTER_USER="%s", MASTER_PASSWORD="%s", MASTER_LOG_FILE="%s", MASTER_LOG_POS=%s;START SLAVE;""" % (master_ip,slave_user,slave_password,log_file,log_pos), 'root', root_passwd)

			else:
				fabric.api.warn(fabric.colors.yellow('The server %s is not available in %s' % (slave,stage)))
			
		# If the replication is True and the 'slave' key is not given then this should be set up
		# as a master database and we should correctly set the values in the my.cnf file
		else:
			# Set up the accepted IP for the slave user
			# default to using '%%', which will open all
			# Note that this relies on having the hostname set correctly, else default is used
			slave_ip = '%%'
			for hostname in PROVIDER['machines'][stage]:
				if 'slave' in PROVIDER['machines'][stage][hostname]['services']['mysql']:
					if PROVIDER['machines'][stage][hostname]['services']['mysql']['slave'] == get_hostname():
						slave_ip = PROVIDER['machines'][stage][hostname]['private_ip'][0]
						break

			# Set up a master conf file and restart
			context = {
				'db_name'    : name,
			}
			template = os.path.join(fabric.api.env.conf['FILES'],'mysqld_master.cnf')
			fabric.contrib.files.upload_template(template,'/etc/mysql/conf.d/',
				context=context,use_sudo=True)
			mysql_restart()

			# Create the slave user for replication and restart
			mysql_execute("""GRANT REPLICATION SLAVE,RELOAD,SUPER ON *.* TO "%s"@"%s" IDENTIFIED BY "%s";FLUSH PRIVILEGES;""" % (slave_user,slave_ip,slave_password), 'root', root_passwd)
			mysql_restart()

			# Get the master status
			mysql_execute("""USE %s;FLUSH TABLES WITH READ LOCK;SHOW MASTER STATUS;""" % (name), 'root', root_passwd)
			fabric.contrib.console.confirm('Write down the log file name and position. Do you want to continue?')
			mysql_execute("""UNLOCK TABLES;""", 'root', root_passwd)

def mysql_start():
	""" Start MySQL """
	service('mysql','start')

def mysql_stop():
	""" Stop MySQL """
	service('mysql','stop')

def mysql_restart():
	""" Restart MySQL """
	service('mysql','restart')

def mysql_execute(sql, user='', password=''):
	"""
	Executes passed sql command using mysql shell.
	"""
	with fabric.api.settings(warn_only=True):
		return fabric.api.run("echo '%s' | mysql -u%s -p%s" % (sql, user, password))

def mysql_create_db(user='',password='',database=''):
	"""
	Creates an empty mysql database. 
	"""
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	if not user:
		user     = fabric.api.prompt('Please enter username:')
	if not database:
		database = fabric.api.prompt('Please enter database name:')
	
	params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
	mysql_execute('CREATE DATABASE %s %s;' % (database, params), user, password)

def mysql_create_user(user='',password='',new_user='',new_password=''):
	""" Create a new mysql user. """
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	if not user:
		user         = fabric.api.prompt('Please enter username:')
	if not new_user:
		new_user     = fabric.api.prompt('Please enter new username:')
	if not new_password:
		new_password = fabric.api.prompt('Please enter new password for %s:' % new_user)

	mysql_execute("""GRANT ALL privileges ON *.* TO "%s" IDENTIFIED BY "%s";FLUSH PRIVILEGES;""" % 
		(new_user, new_password), user, password)

def mysql_drop_user():
	""" Drop a mysql user. """
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	user      = fabric.api.prompt('Please enter username:')
	drop_user = fabric.api.prompt('Please enter username to drop:')

	mysql_execute("DROP USER %s;" % (drop_user), user)

def mysql_dump():
	""" Runs mysqldump. Result is stored at /srv/active/sql/ """
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	dir = '/srv/active/sql/'
	fabric.api.run('mkdir -p %s' % dir)
	now = datetime.now().strftime("%Y.%m.%d-%H.%M")
	
	user     = fabric.api.prompt('Please enter username:')
	database = fabric.api.prompt('Please enter database name:')
	
	fabric.api.run('mysqldump -u%s -p %s > %s' % (user, database,
		os.path.join(dir, '%s-%s.sql' % (database, now))))

def mysql_load(filename):
	""" Load MySQL Database with 'mysql DATABASENAME < filename.sql' """
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	user     = fabric.api.prompt('Please enter username:')
	database = fabric.api.prompt('Please enter database name:')
	fabric.api.run('mysql %s -u%s -p < %s' % (database, user, filename))

def list_sql_files():
	""" List available sql files in active project """
	fabric.api.run('ls /srv/active/sql')

def mysql_backup():
	""" Backup the database """
	if not _mysql_is_installed():
		fabric.api.warn(fabric.colors.yellow('MySQL must be installed.'))
		return

	fabric.api.run('automysqlbackup')

