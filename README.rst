=========================================
django-fab-deploy: django deployment tool
=========================================

red-fab-deploy is a collection of Fabric scripts for deploying and
managing django projects on Debian/Ubuntu servers. License is MIT.

This project is a fork of django-fab-deploy.

Please read the `docs <http://packages.python.org/django-fab-deploy>`
for more info.

These tools are being geared towards deploying on Amazon EC2, however 
there are steps to set up Rackspace to work with these tools.

Rackspace Setup
===============

1. Make an ssh key pair and put it in the project /deploy folder with
   names that are recognizable.

2. Make a fab file using the example fabfile in the project and place
   it in the top level directory of your project.

3. To create the ubuntu user run the following command::

       $ fab dev rackspace_as_ec2:"/deploy/id_pub"

4. If this is the first time deploying on the server run the following::

       $ fab dev full_deploy:"tagname"

   Here "tagname" is the name of the tagged version of the code you wish
   to deploy.  This code must reside in the /repo/tags/ directory.
   
   If this is not the first time you are deploying on the server then run::

       $ fab dev deploy_project:"tagname"
       $ fab dev make_active:"tagname"

5. Next you'll want to get the server going::

       $ fab dev web_server_setup web_server_start

6. Now everything should be running

