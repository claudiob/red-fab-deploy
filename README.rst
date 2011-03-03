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

2. Copy the fabfile_example.py file from the project to the top level directory of your project, then edit specifying your INSTANCE_NAME, REPO and SERVER

3. To create the ubuntu user run the following command::

       $ fab dev rackspace_as_ec2:"deploy/id_pub"

   and press ENTER to every question, but write *www-data* to "Enter the group name you want to add the user to:"   

4. **If this is the first time** deploying on the server run the following::

       $ fab dev full_deploy:"tagname" -i deploy/[your private SSH key here]
       
   Here "tagname" is the name of the tagged version of the code you wish
   to deploy.  This code must reside in the /repo/tags/ directory.
   If you have not created a tag yet, do it with::

      $ svn copy trunk tags/release-0.0.1; svn ci -m "Tagging 'trunk' for django-fab-deploy to work."

   For the source code to be installed from the SVN repository to the server you need to enter your SVN credentials.
   
   **If this is not the first time** you are deploying on the server then run::

       $ fab dev deploy_project:"tagname" -i deploy/[your private SSH key here]
       $ fab dev make_active:"tagname" -i deploy/[your private SSH key here]

5. Next you'll want to get the server going
  **If this is the first time** deploying on the server run the following::
  Edit deploy/uwsgi.ini and substitute 127.0.0.1 with the local IP address of the production machine.
  Edit deploy/nginx.conf and substitute the 127.0.0.1 in the upstream django server with the local IP address and the 127.0.0.1 in the server_name with the remote IP address of the production machine.
  Then launch::
  
       $ fab dev web_server_setup web_server_start -i deploy/[your private SSH key here]

  **If this is not the first time** then just run::

       $ fab dev uwsgi_restart -i deploy/[your private SSH key here]
       $ fab dev web_server_restart -i deploy/[your private SSH key here]
  
6. Next you'll have to run the commands to have the application running, such as::

       $ fab dev manage:syncdb -i deploy/[your private SSH key here]
       $ fab dev manage:loaddata test -i deploy/[your private SSH key here]

7. Now everything should be running
