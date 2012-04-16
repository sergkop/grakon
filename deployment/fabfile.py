import json
import os.path
import StringIO

from fabric.api import cd, env, get, local, prefix, put, run, sudo

REPOSITORY = 'git@github.com:sergkop/grakon.git'
# TODO: set env attributes like in http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user
# TODO: run commands specifying the user (first root, then user)

# TODO: user 'deluser --remove-home' to remove user

# TODO: start using roles

# TODO: separate root access settings and non-root
USERNAME = 'serg' # TODO: move it to settings, use paths relative to home dir

CONFIG_FILE_PATH = '/home/serg/data/grakon/passwords/config.json' # TODO: take it as an argument

conf = json.load(open(CONFIG_FILE_PATH))

env.hosts = conf['servers'].keys()
env.passwords = conf['servers'] # set passwords for accessing servers

# TODO: Commands for: restart all services, update code (static files, migrate, restart server, etc.)

def virtualenv(command):
    with prefix('source %s' % os.path.join('/home/%s' % USERNAME, conf['env_path'], 'bin', 'activate')):
        run(command)

def init_data_server():
    ubuntu_packages = ['postgresql', 'postgresql-client', 'memcached']

    sudo('aptitude -y install %s' % ' '.join(ubuntu_packages))
    # TODO: configure psql and memcached, init database

def cmd(command):
    # TODO: solve 'mesg: /dev/pts/1: Operation not permitted'
    return sudo(command, user=USERNAME)

# TODO: what if it has already been run on a server?
def init_system():
    # TODO: block password access (for all accounts), add server ip to mysql's server whitelist,
    #       close ports, activate firewall, add server to load balancer list, reboot server after upgrade (optional),
    #       configure services (nginx, etc.)
    #       set files permissions, install sentry,
    #       minify static files, set different cache time headers for static files

    # Install libraries and applications
    ubuntu_packages = [
        # Python
        'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

        # Utils
        'gcc', 'git', 'graphviz', 'mc', 'htop',

        # Services
        'nginx',

        # Libraries
        'libxslt-dev', 'graphviz-dev', 'python-dev', # 'libmysqlclient-dev',
    ]

    sudo('aptitude -y update')
    sudo('aptitude -y upgrade')
    sudo('aptitude -y install %s' % ' '.join(ubuntu_packages))

    # Create user
    sudo('useradd -s /bin/bash -d /home/%(user)s -m %(user)s -p %(password)s' % {
            'user': USERNAME, 'password': env.passwords[env.host_string]})

    # Set default text editor
    cmd('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /home/%s/.selected_editor' % USERNAME)
    sudo('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /root/.selected_editor')

    # Make user sudoer
    sudo('echo "%s ALL=(ALL:ALL) ALL" >> /etc/sudoers' % USERNAME)

    # Generate ssh key
    cmd('mkdir /home/%s/.ssh' % USERNAME)
    cmd('ssh-keygen -t rsa -f /home/%s/.ssh/id_rsa -N %s -C "%s"' % (
            USERNAME, conf['SSH_KEY_PASSPHRASE'], conf['GITHUB_EMAIL']))

    # TODO: automate it
    print "Copy the following public key and add it to the list of deploy keys on github (https://github.com/sergkop/grakon/admin/keys)"
    cmd('cat /home/%s/.ssh/id_rsa.pub' % USERNAME)

    # Test access to repo
    cmd('ssh -T git@github.com') # TODO: make sure this test is positive

    # Add developers ssh keys to access account
    cmd('echo "%s" >> /home/%s/.ssh/authorized_keys' % ('\n'.join(conf['developers_ssh_pubkey']), USERNAME))

def prepare_code():
    code_path = os.path.join('/home/%s' % USERNAME, conf['code_path'])
    env_path = os.path.join('/home/%s' % USERNAME, conf['env_path'])
    static_path = os.path.join('/home/%s' % USERNAME, conf['static_path'])

    cmd('mkdir -p %s %s %s' % (code_path, env_path, static_path))

    # TODO: if code is already there - make git pull and update it
    cmd('git clone %s %s' % (REPOSITORY, code_path))

    # Create settings file
    settings_content = StringIO.StringIO()
    get(os.path.join(code_path, 'grakon', 'site_settings.py.example'), settings_content)

    put(StringIO.StringIO(settings_content.read() % conf),
            os.path.join(code_path, 'grakon', 'site_settings.py'))

    #with open(os.path.join(code_path, 'grakon', 'site_settings.py'), 'w') as f:
    #    f.write(settings_code % conf)

    # Create virtualenv
    run('virtualenv --no-site-packages %s' % env_path)

    # TODO: problems setting up pygraphviz (need to specify proper include paths)
    virtualenv('pip install -r %s' % os.path.join(code_path, 'deployment', 'requirements.txt'))
