from fab_deploy.server.apache import (apache_touch_wsgi, apache_make_wsgi,
	apache_restart, apache_install, apache_make_config, apache_setup,
	apache_setup_locale, )
from fab_deploy.server.nginx import (nginx_install, nginx_setup,
	nginx_start, nginx_stop, nginx_restart, )
from fab_deploy.server.uwsgi import (uwsgi_install, uwsgi_setup,
	uwsgi_start, uwsgi_stop, uwsgi_restart, )
