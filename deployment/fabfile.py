import json
import os.path

from fabric.api import cd, env, local, prefix, run, sudo

REPOSITORY = 'git@github.com:sergkop/grakon.git'
# TODO: set env attributes like in http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user
# TODO: run commands specifying the user (first root, then user)

USERNAME = 'serg' # TODO: move it to settings

CONFIG_FILE_PATH = '/home/serg/data/grakon/passwords/config.json' # TODO: take it as an argument

conf = json.load(open(CONFIG_FILE_PATH))

env.hosts = conf['servers'].keys()
env.passwords = conf['servers'] # set passwords for accessing servers

# TODO: Commands for: restart all services, update code (static files, migrate, restart server, etc.)

def virtualenv(command):
    with prefix('source %s' % os.path.join(conf['env_path'], 'bin', 'activate')):
        run(command)

def init_mysql_server():
    # TODO: configure mysql and memcached, init database

# TODO: what if it has already been run on a server?
def init_system():
    # TODO: block password access (for all accounts), add server ip to mysql's server whitelist,
    #       close ports, activate firewall, add server to load balancer list, configure services (nginx, etc.)
    #       set files permissions, install sentry,
    #       minify static files, set different cache time headers for static files

    # Install libraries and applications
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

    # Create user
    sudo('useradd -s /bin/bash -d /home/%(user)s -m %(user)s -p %(password)s' % {
            'user': USERNAME, 'password': env.host_string})s

    # Set default text editor
    # TODO: do it on a server, not client
    with open('/home/%s/.selected_editor' % USERNAME, 'w') as f:
        f.write('SELECTED_EDITOR="/usr/bin/mcedit"')

    # Make user sudoer
    sudo('echo "%s ALL=(ALL:ALL) ALL" >> /etc/sudoers' % USERNAME)

    # Generate ssh key
    run('ssh-keygen -t rsa -f /home/%s/.ssh/id_rsa -N %s -C "%s"' % (
            USERNAME, SSH_KEY_PASSPHRASE, EMAIL))

    # TODO: add public key to github project and test access "ssh -T git@github.com"

    # Add developer's ssh key
    for developer_key in DEVELOPER_PUBKEYS:
        run('echo "%s" >> /home/%s/.ssh/authorized_keys' % (developer_key, USERNAME))

def prepare_code():
    run('mkdir -p %s' % conf['code_path'])
    run('mkdir -p %s' % conf['env_path'])

    # TODO: if code is already there - make git pull and update it
    run('git clone %s %s' % (REPOSITORY, conf['code_path']))

    # Create settings file
    settings_code = open(os.path.join(conf['code_path'], 'grakon', 'site_settings.py.example')).read()

    with open(os.path.join(conf['code_path'], 'grakon', 'site_settings.py'), 'w') as f:
        f.write(settings_code % conf)

    # Create virtualenv
    run('virtualenv --no-site-packages %s' % conf['env_path'])

    virtualenv('pip install -r %s' % os.path.join(conf['code_path'], 'deployment', 'requirements.txt'))
