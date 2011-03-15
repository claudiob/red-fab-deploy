=========================================
django-fab-deploy: django deployment tool
=========================================

red-fab-deploy is a collection of Fabric scripts for deploying and
managing django projects on Debian/Ubuntu servers. License is MIT.

This project was inspired by `django-fab-deploy <http://packages.python.org/django-fab-deploy>`
and `cuisine <https://github.com/ff0000/cuisine/>`.

These tools are being geared towards deploying on Amazon EC2, however 
there are steps to set up Rackspace and other hosts to work with these tools.

Advanced AWS Setup
==================

Development
***********

There now exists a set of advanced tools for streamlining the setup of 
cloud servers and project deployment.  Follow these steps:

1. Ensure you have the following in your fabfile conf settings: INSTANCE_NAME,
PROVIDER, REPO and either (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) or 
(RACKSPACE_USER, RACKSPACE_KEY).

2. To set up your AWS account you must run the following::

    $ fab generate_config
    $ fab go

This sets up your config file, creates a default ec2 key file, authorizes port 22 with
the default security group, and then deploys 1 development node server to your account.

2. You must wait until all your instances have spawned before going further.  This could take 
up to 5 minutes.

3. To install all the correct software on your new development node run the following::

    $ fab -i deploy/[your private SSH key here] set_hosts go_setup

This will grab all the development node ip addresses, set them as hosts, and then run
a software setup package on each of the servers based on the generated config file.

4. Next you want to deploy to the development server by running the following::

    $ fab -i deploy/[your private SSH key here] set_hosts go_deploy

This will put the trunk of your repo onto each machine with server software and make it active.
Be aware that this will remove any current version of trunk that is currently deployed.

Production
**********

Production is almost identical to development, except for the following::

    $ fab generate_config
    $ fab go:production
    $ fab -i deploy/[your private SSH key here] set_hosts:production go_setup:stage=production
    $ fab -i deploy/[your private SSH key here] set_hosts:production go_deploy:stage=production,tagname=tag

Cloud Server Setup
==================

Amazon Deployment
*****************

These steps will help you deploy cloud servers:

1. Currently you can deploy to either rackspace or amazon cloud servers using
   libcloud.  In your env.conf place the following::

    PROVIDER = 'amazon'

2. Place the access keys in your env.conf::

    AWS_ACCESS_KEY_ID     = 'yourawsaccesskeyid',
    AWS_SECRET_ACCESS_KEY = 'yourawssecretaccesskey',

3. You can now run any commands to get information your your cloud servers.

4. When deploying on amazon you must create a security key::

    fab ec2_create_key:"yourkeyname"

5. You cannot get ssh access unless you add ports to the default security group::

    fab ec2_authorize_port:"default,tcp,22"

6. To deploy development or production nodes run one of the following commands::

    fab deploy_nodes:"development"
    fab deploy_nodes:"production"

7. Your cloud servers should now be operational.

Rackspace Deployment
********************

These steps will help you deploy cloud servers:

1. Currently you can deploy to either rackspace or amazon cloud servers using
   libcloud.  In your env.conf place the following::

    PROVIDER = 'rackspace'

2. Place the access keys in your env.conf::

    RACKSPACE_USER = 'yourrackspaceclouduser',
    RACKSPACE_KEY  = 'yourrackspacecloudkey',

3. You can now run any commands to get information your your cloud servers.

4. To deploy development or production nodes run one of the following commands::

    fab deploy_nodes:"development"
    fab deploy_nodes:"production"

5. Your cloud servers should now be operational.

Rackspace Setup
===============

1. Make an ssh key pair and put it in the project /deploy folder with
   names that are recognizable.

2. Copy the fabfile_example.py file from the project to the top level 
   directory of your project, then edit specifying your INSTANCE_NAME,
   REPO and SERVER

3. To create the ubuntu user run the following command::

       $ fab dev provider_as_ec2

   and press ENTER to every question.  This will generate a DSA key pair
   with names 'ubuntu.id_dsa' and 'ubuntu.id_dsa.pub'.  Add these to your
   project and don't lose it.  This is the private SSH key you will use in 
   the following steps.

4. **If this is the first time** deploying on the server run the following::

       $ fab -i deploy/[your private SSH key here] dev deploy_full:"tagname"
       
   Here "tagname" is the name of the tagged version of the code you wish
   to deploy.  This code must reside in the /repo/tags/ directory.
   If you have not created a tag yet, do it with::

       $ svn copy trunk tags/release-0.0.1; svn ci -m "Tagging 'trunk' for django-fab-deploy to work."

   For the source code to be installed from the SVN repository to the 
   server you need to enter your SVN credentials.
   
   **If this is not the first time** you are deploying on the server then run::

       $ fab -i deploy/[your private SSH key here] dev deploy_project:"tagname" 
       $ fab -i deploy/[your private SSH key here] dev make_active:"tagname"

5. Next you'll want to get the server going.

   **If this is the first time** deploying on the server run the following::

       Edit deploy/uwsgi.ini and substitute 127.0.0.1 with the local IP 
       address of the production machine.
       Edit deploy/nginx.conf and substitute the 127.0.0.1 in the upstream 
       django server with the local IP address and the 127.0.0.1 in the 
       server_name with the remote IP address of the production machine.
  
   Then launch::
  
       $ fab dev web_server_setup web_server_start -i deploy/[your private SSH key here]

   **If this is not the first time** then just run::

       $ fab -i deploy/[your private SSH key here] dev uwsgi_restart
       $ fab -i deploy/[your private SSH key here] dev web_server_restart
  
6. Next you'll have to run the commands to have the application running, such as::

       $ fab -i deploy/[your private SSH key here] dev manage:syncdb 
       $ fab -i deploy/[your private SSH key here] dev manage:loaddata test

7. Now everything should be running

Database Setup
==============

The databases supported with red-fab-deploy are MySQL and PostgreSQL

MySQL Setup
***********

To install and setup mysql you'll need to run the following commands::

       $ fab -i deploy/[your private SSH key here] dev mysql_install
       $ fab -i deploy/[your private SSH key here] dev mysql_create_db
       $ fab -i deploy/[your private SSH key here] dev mysql_create_user

PostgreSQL
**********

The PostgreSQL commands are not yet set up

