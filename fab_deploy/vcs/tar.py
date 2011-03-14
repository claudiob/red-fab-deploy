from datetime import datetime
import os.path

import fabric.api

def _exclude_string():
    excludes = ['config.py', '*.pyc', '*.pyo', '*.swp', '.svn/']
    exclude_string = " ".join(['--exclude "%s"' % pattern for pattern in excludes])
    if os.path.exists('.excludes'):
        exclude_string =  "-X .excludes %s" % exclude_string
    return exclude_string

def push(tagname,**kwargs):
    """
    Upload the current project to a remote system, tar/gzipping during the move.
    Files listed at :file:`<project root>/.exclude` file wouldn't be uploaded
    (glob patterns are supported in .exclude file).

    This function makes use of the ``/tmp/`` directory and the ``tar`` and
    ``gzip`` programs/libraries; thus it will not work too well on Win32
    systems unless one is using Cygwin or something similar.

    This should be using ``fabric.contrib.project.upload_project``
    but upload_project doesn't support excludes.
    """
    tar_file = "/tmp/fab.%s.tar" % datetime.utcnow().strftime(
        '%Y_%m_%d_%H-%M-%S')
    fabric.api.local("tar %s -czf %s /tmp/%s" % (_exclude_string(), tar_file, tagname))
    tgz_name = '%s/%s.tar.gz' % (fabric.api.env.conf.SRC_DIR, fabric.api.env.conf.INSTANCE_NAME)
    fabric.api.put(tar_file, tgz_name)
    fabric.api.local("rm -f %s" % tar_file)
    with fabric.api.cd(fabric.api.env.conf.SRC_DIR):
        fabric.api.run("tar -xzf %s" % tgz_name)
        fabric.api.run("rm -f %s" % tgz_name)

