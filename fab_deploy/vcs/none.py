import os.path
from datetime import datetime
from fabric.api import *

BRANCH_OPTION = None

def _exclude_string():
    excludes = ['config.py', '*.pyc', '*.pyo']
    exclude_string = " ".join(['--exclude "%s"' % pattern for pattern in excludes])
    if os.path.exists('.excludes'):
        exclude_string =  "-X .excludes " + exclude_string
    return exclude_string

def init():
    pass

def up(branch):
    pass

def push():
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
    local("tar %s -czf %s ." % (_exclude_string(), tar_file))
    tgz_name = env.conf.SRC_DIR + '/' + env.conf.INSTANCE_NAME + ".tar.gz"
    put(tar_file, tgz_name)
    local("rm -f " + tar_file)
    with cd(env.conf.SRC_DIR):
        run("tar -xzf " + tgz_name)
        run("rm -f " + tgz_name)

def configure():
    pass

