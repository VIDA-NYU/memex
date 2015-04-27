from fabric.api import env, local, lcd, shell_env
from fabric.colors import red, green
from fabric.decorators import task, runs_once
from fabric.utils import abort, puts

import fileinput
import os
import sys

PROJ_ROOT = os.path.dirname(env.real_fabfile)
MEMEX_ROOT = os.path.join(PROJ_ROOT, '..')
env.project_name = 'seed_crawler'
env.python = 'python' if 'VIRTUAL_ENV' in os.environ else 'venv/bin/python'
env.nltk_data = os.path.join(PROJ_ROOT, 'nltk_data')
env.pythonpath = os.pathsep.join([
    os.path.join(PROJ_ROOT, 'seeds_generator', 'src'),
    '.'])


@task
def setup():
    """
    Set up a local development environment

    This command must be run with Fabric installed globally (not inside a
    virtual environment)
    """
    if os.getenv('VIRTUAL_ENV') or hasattr(sys, 'real_prefix'):
        abort(red('Deactivate any virtual environments before continuing.'))
    make_settings()
    make_virtual_env()
    install_nltk_data()
    compile_seeds_generator()
    #install_node_packages()
    puts(green('Development environment successfully created.'))

@task
@runs_once
def make_settings():
    """
    Generate a local settings file.

    Without any arguments, this file will go in vis/config.conf.
    """
    with lcd(PROJ_ROOT):
        settings_file = 'vis/config.conf'
        local('if [ ! -f {0} ]; then cp {1} {0}; fi'.format(
            settings_file, 'vis/config.conf-in'))
        for line in fileinput.input(settings_file, inplace=True):
            puts(line.replace("tools.staticdir.root = .",
                              "tools.staticdir.root = {0}/{1}".format(
                                  PROJ_ROOT, 'vis/html')))

@task
def runserver():
    "Run the development server"
    with lcd(PROJ_ROOT), shell_env(NLTK_DATA=env['nltk_data'],
                                   PYTHONPATH=env['pythonpath'],
                                   MEMEX_HOME=MEMEX_ROOT):
        local('{python} sourcepin_api/seed_crawler_model.py'.format(**env))
        #local('{python} manage.py runserver --traceback'.format(**env))

@task
def runvis():
    "Run the development server"
    with lcd(PROJ_ROOT), shell_env(NLTK_DATA=env['nltk_data'],
                                   PYTHONPATH=env['pythonpath'],
                                   MEMEX_HOME=MEMEX_ROOT):
        local('{python} vis/server.py'.format(**env))

def make_virtual_env():
    "Make a virtual environment for local dev use"
    with lcd(PROJ_ROOT):
        local('virtualenv --system-site-packages venv')
        local('venv/bin/pip install -r requirements.pre.txt')
        local('venv/bin/pip install -r requirements.txt')

def install_node_packages():
    "Install requirements from NPM."
    with lcd(PROJ_ROOT):
        local('npm install')

def install_nltk_data():
    "Install data files for NLTK."
    with lcd(PROJ_ROOT), shell_env(NLTK_DATA=env['nltk_data']):
        local("if [ ! -d {nltk_data} ]; then mkdir {nltk_data}; fi".format(**env))
        local('if [ ! -d {nltk_data}/chunkers ]; then {python} -m nltk.downloader -d {nltk_data} all; fi'.format(**env))


def compile_seeds_generator():
    "Compile the sees generator."
    with lcd(PROJ_ROOT + '/seeds_generator'):
        local('sh compile.sh')
