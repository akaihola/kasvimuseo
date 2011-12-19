from fabric.api import env, task
from djangodeploy import (bootstrap,
                          clone_db,
                          configure_nginx,
                          configure_postgresql,
                          configure_supervisor,
                          collectstatic,
                          create_db,
                          create_db_user,
                          install_django,
                          install_project,
                          migrate,
                          restart_django,
                          syncdb,
                          update,
                          update_code)


@task
def kala():
    env.hosts = ['kala.ambitone.com']
    env.project_root = '/www/ylaneenkasvit'
    env.site_root = '/www/ylaneenkasvit'
    env.project_name = 'ylaneenkasvit'
    env.www_hostnames = ['kasvit.ambitone.com']
    env.wsgi_port = 25121
    env.repository = 'nopo.ambitone.com:/var/lib/git/repositories/ylaneenkasvit.git'
    env.db_name = 'ylaneenkasvit'
    env.db_user = 'ylaneenkasvit'
    env.nginx_root_location_extra = 'client_max_body_size 10m;'
    env.gunicorn_timeout = 240
    env.django_settings_module = 'ylaneenkasvit.ylaneenkasvit_settings'
    env.media_sites = [
        {'name': 'ylaneenkasvit-static',
         'www_hostnames': ['static.kasvit.ambitone.com'],
         'root': '{project_root}/static/'.format(**env)},
        {'name': 'ylaneenkasvit-media',
         'www_hostnames': ['media.kasvit.ambitone.com'],
         'root': '{project_root}/media/'.format(**env)}]
