from fabric.api import env
from ambideploy import bootstrap, clone_db, install_django, install_project


def kala():
    env.hosts = ['kala.ambitone.com']
    env.project_root = '/www/ylaneenkasvit'
    env.project_name = 'ylaneenkasvit'
    env.repository = 'nopo.ambitone.com:/var/lib/git/repositories/ylaneenkasvit.git'
    env.db_name = 'ylaneenkasvit'
    env.db_user = 'ylaneenkasvit'
