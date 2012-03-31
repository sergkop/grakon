import json
import os.path

from fabric.api import cd, env, local, prefix, run, sudo

REPOSITORY = 'git@github.com:sergkop/grakon.git'
# TODO: set env attributes like in http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user

CONFIG_FILE_PATH = '/home/serg/data/grakon/passwords/config.json' # TODO: take it as an argument

conf = json.load(open(CONFIG_FILE_PATH))

env.hosts = conf['servers'].keys()
env.passwords = conf['servers'] # set passwords for accessing servers

# TODO: Commands for: restart all services, update code (static files, migrate, restart server, etc.)

def virtualenv(command):
    with prefix('source %s' % os.path.join(conf['env_path'], 'bin', 'activate')):
        run(command)

def init_system():
    # TODO: create user serg, home directory, add ssh key of developer to be able to access it,
    #       set bash as default shell, make it sudoer, put ssh key to access git repository from the server
    #       create directories, install required software, add server ip to mysql's server whitelist,
    #       close ports, activate firewall, (add server to load balancer list), configure services (nginx, postfix, etc.)
    #       set files permissions, set .selected_editor, init database (optional), install sentry,
    #       minify static files, set different cache time headers for static files
    run('mkdir -p %s' % conf['code_path'])
    run('mkdir -p %s' % conf['env_path'])

    ubuntu_packages = [
        # Python
        'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

        # Utils
        'gcc', 'git', 'graphviz', 'mc',

        # Services
        'nginx',

        # Libraries
        'libmysqlclient-dev', 'libxslt-dev', 'graphviz-dev', # python-dev?
    ]

    sudo('aptitude install %s' % ' '.join(ubuntu_packages))

def prepare_code():
    # TODO: if code is already there - make git pull and update it
    run('git clone %s %s' % (REPOSITORY, conf['code_path']))

    # Create settings file
    settings_code = open(os.path.join(conf['code_path'], 'grakon', 'site_settings.py.example')).read()

    with open(os.path.join(conf['code_path'], 'grakon', 'site_settings.py'), 'w') as f:
        f.write(settings_code % conf)

    # Create virtualenv
    run('virtualenv --no-site-packages %s' % conf['env_path'])

    virtualenv('pip install -r %s' % os.path.join(conf['code_path'], 'deployment', 'requirements.txt'))

def host_type():
    run('source /home/serg/env/grakon/bin/activate')
    #run('ls /home/serg/')
    #run('cp -r /home/serg/sites/grakon_site/ /home/serg/tempdata/grakon_site1/')
