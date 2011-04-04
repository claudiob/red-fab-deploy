# django-fab-deploy: django deployment tool

red-fab-deploy is a collection of Fabric scripts for deploying and
managing django projects on Debian/Ubuntu servers. License is MIT.

This project is specifically targeted at deploying websites built using
the `pypeton <https://github.com/ff0000/pypeton>` project creation tool.
Basically this means you must follow the same folder and file layout as
found in that tool.

This project was inspired by `django-fab-deploy <http://packages.python.org/django-fab-deploy>`
and `cuisine <https://github.com/ff0000/cuisine/>`.

These tools are being geared towards deploying on Amazon EC2, however 
there are steps to set up Rackspace and other hosts to work with these tools.

## Installation

IMPORTANT: red-fab-deploy will only work if you install the following packages:
    
	$ pip install -e git+git://github.com/bitprophet/fabric.git#egg=fabric
	$ pip install -e git+git://github.com/apache/libcloud.git@trunk#egg=libcloud
	$ pip install boto
	$ pip install -e git+git://github.com/ff0000/red-fab-deploy.git#egg=red-fab-deploy

Be aware that the dependencies are Fabric>=1.0 and apache-libcloud>=0.4.3.  These
packages are at the cutting edge and without them you will see things break.

## Important Notes

Configuration files for apache, nginx, and uwsgi must follow a very common naming
convention.  These files all should be found in the /deploy/ folder in side of
the project.  Simply put, the files must describe the stage by using the 
convention 'filename.<stage>.[ini|conf]', where <stage> can be
'production, 'staging', or 'development'.  You can choose the names of your stages
for your individual project, but they must conform to the stages found in the 
generated config file.

For example, the nginx.conf file for production will be named 'nginx.production.conf',
whereas the nginx.conf file for development will be named 'nginx.development.conf'.
If these two files are the same then it's recommended that you write one file named
'nginx.conf' and check in symlinks 'nginx.<stage>.conf' into the same folder.

Following this convention will make deployment much less of a hassle and hopefully
will prevent the need to log into the servers.

## Advanced Deployment and Setup

### Fabfile

The first thing you need to do is set up your fabfile.  This project includes an example
that is necessary to get started called fabfile_example.py.  You can take a look at it and 
replace the default values with your actual values.

Importantly there are different settings for setting up Amazon EC2 instances or Rackspace
Cloud instances.  These settings are listed below:

	PROVIDER = 'amazon'
	AWS_ACCESS_KEY_ID     = 'yourawsaccesskeyid',
	AWS_SECRET_ACCESS_KEY = 'yourawssecretaccesskey',

Or the following settings for Rackspace:

	PROVIDER = 'rackspace'
	RACKSPACE_USER = 'yourrackspaceclouduser',
	RACKSPACE_KEY  = 'yourrackspacecloudkey',

As an example here is the env.conf dictionary for amazon that you'd find in your file:

	env.conf = dict(
		# THIS IS YOUR PROVIDER AND ACCESS
		PROVIDER = 'ec2_us_east',
		AWS_ACCESS_KEY_ID     = '',     
		AWS_SECRET_ACCESS_KEY = '',     
		
		# THESE THREE ARE NECESSARY
		CONF_FILE = os.path.join(os.getcwd(),'fabric.conf'),
		INSTANCE_NAME = 'projectname', 
		REPO = 'http://some.repo.com/projectname/',
	)

### Development

There now exists a set of advanced tools for streamlining the setup of 
cloud servers and project deployment.  Follow these steps:

1. Ensure you have correctly set up your fabfile using the instructions above.

2. To begin with the set up of your cloud account you must run the following commands. On
AWS only this will create a default key file and authorize tcp ports 22 and 80 for use.  With
Rackspace setup the key file will not be created so you must follow instructions in step 4.

		$ fab generate_config
		$ fab go:development
		$ fab update_nodes # might need to wait a minute and run this

3. You must wait until all your instances have spawned before going further.  This could take 
up to 5 minutes.  You must also wait until you have the root password if you are using Rackspace,
which usually comes in an email a few minutes later.

4. If you are running Rackspace you must run this next set of commands.  This will create a 
default key file, create and set up a user, add the user to the default security group, 
and then grant sudo access.  Finally, it will copy that key into the authorized_keys file for 
each machine you've created the user on.

		$ fab ssh_local_keygen:"rackspace.development"
		$ fab set_hosts:development,root provider_as_ec2:username=ubuntu
		$ fab set_hosts:development,root ssh_authorize:username=ubuntu,key=deploy/rackspace.development.pub

5. To install all the correct software on your new development node run the following:

		$ fab -i deploy/[your private SSH key here] set_hosts:development go_setup:development

	This will grab all the development node ip addresses, set them as hosts, and then run
	a software setup package on each of the servers based on the generated config file.

6. Next you want to deploy to the development server by running the following:

		$ fab -i deploy/[your private SSH key here] set_hosts:development go_deploy:development,tag

	This will put the trunk of your repo onto each machine with server software and make it active.
	Be aware that this will remove any current version of trunk that is currently deployed.

### Production

Production is almost identical to development, except for the following:

	$ fab generate_config # Do not overwrite an earlier file
	$ fab go:production
	$ fab update_nodes # might need to wait a minute and run this
	$ fab ssh_local_keygen:"rackspace.production"
	$ fab set_hosts:production,root provider_as_ec2:username=ubuntu
	$ fab set_hosts:production,root ssh_authorize:username=ubuntu,key=deploy/rackspace.production.pub
	$ fab -i deploy/[your private SSH key here] set_hosts:production go_setup:production
	$ fab -i deploy/[your private SSH key here] set_hosts:production go_deploy:production,tag

NOTE: If you already have generated a config for deployment DO NOT generate another config file.
This is very important as you may overwrite the original and lose the information you have inside
of it.  Furthermore, you'll want to check in the config file into your repository.

## Deploying on the Server

### The Code Manually

*If this is the first time* deploying on the server run the following:

	fab -i deploy/[your private SSH key here] dev deploy_full:"tagname"
    
Here "tagname" is the name of the tagged version of the code you wish
to deploy.  This code must reside in the /repo/tags/ directory.
If you have not created a tag yet, do it with::

	svn copy trunk tags/release-0.0.1; svn ci -m "Tagging 'trunk' for django-fab-deploy to work."

For the source code to be installed from the SVN repository to the 
server you need to enter your SVN credentials.

*If this is not the first time* you are deploying on the server then run:

	fab -i deploy/[your private SSH key here] dev deploy_project:"tagname" 
	fab -i deploy/[your private SSH key here] dev make_active:"tagname"

### The Server

*If this is the first time* deploying on the server run the following:

	* Edit deploy/uwsgi.ini and substitute 127.0.0.1 with the local IP address of the production machine.
	* Edit deploy/nginx.conf and substitute the 127.0.0.1 in the upstream django server with the local IP address and the 127.0.0.1 in the server_name with the remote IP address of the production machine.

Then launch:

	fab dev web_server_setup web_server_start -i deploy/[your private SSH key here]

**If this is not the first time** then just run::

	fab -i deploy/[your private SSH key here] dev uwsgi_restart
	fab -i deploy/[your private SSH key here] dev web_server_restart
  
Next you'll have to run the commands to have the application running, such as:

	fab -i deploy/[your private SSH key here] dev manage:syncdb 
	fab -i deploy/[your private SSH key here] dev manage:loaddata test

## Database Setup

The databases supported with red-fab-deploy are MySQL and PostgreSQL.

### Important Setup

By default red-fab-deploy will set to values inside of fabric.api.env.conf:

	DB        = 'mysql' # 'postgresql' is also allowed
	DB_PASSWD = 'password'

These indicate that the database type being used is 'mysql' and that the
database password for the root user is 'password'.  BE AWARE THAT THIS IS 
ENTIRELY INSECURE.  If you are installing any databases you should put the
'DB_PASSWD' setting inside your fabfile inside of the env.conf dictionary
and change the value from 'password' to something secure.  You can also set
this value to an empty string if you want to always be prompted for a 
password.

### MySQL Setup

To install and setup mysql you'll need to run the following commands::

	fab -i deploy/[your private SSH key here] dev mysql_install
	fab -i deploy/[your private SSH key here] dev mysql_create_db
	fab -i deploy/[your private SSH key here] dev mysql_create_user

### PostgreSQL

The PostgreSQL commands are not yet set up

