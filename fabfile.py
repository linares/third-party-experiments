from fabric.api import *
from fabric.contrib.console import confirm
import fabric.operations
import time

# Global env settings
env.git_repo = "git@github.com:brelig/infoscout.git"


def dev():
    
    """ staging dev server settings """
    env.hosts = ['staging@staging.infoscoutinc.com']
    env.source_root = '/var/www/dev'
    env.project_root = env.source_root + '/infoscout/pricescout'
    env.activate = 'source /var/www/dev/infoscout/pricescout/ve/bin/activate'
    env.deploy_user = 'staging'    
    env.settings_module = 'infoscout.pricescout.envsettings.dev'
    env.apache_conf = 'infoscout-dev'
    env.celeryd_conf = env.project_root + '/celeryd/config_dev'
    
def staging():
    
    """ staging dev server settings """
    env.hosts = ['staging@staging.infoscoutinc.com']
    env.source_root = '/var/www/staging'
    env.project_root = env.source_root + '/infoscout/pricescout'
    env.activate = 'source /var/www/staging/infoscout/pricescout/ve/bin/activate'
    env.deploy_user = 'staging'    
    env.branch = 'shoparoo2'
    env.settings_module = 'infoscout.pricescout.envsettings.staging'
    env.celeryd_conf = env.project_root + '/celeryd/config_staging'
    env.apache_conf = 'infoscout-staging'
    env.other_apache_confs = [(env.source_root+'/infoscout/shoparoo', 'shoparoo-staging'),
                              (env.source_root+'/infoscout/receipthog','receipthog-staging')
                              ]
    
def prod():
    """ prod dev server settings """
    env.hosts = ['prod@184.169.145.240', 'prod@184.169.148.63']
    env.source_root = '/var/www/prod'
    env.project_root = env.source_root + '/infoscout/pricescout'
    env.activate = 'source /var/www/prod/infoscout/pricescout/ve/bin/activate'
    env.deploy_user = 'prod'    
    env.settings_module = 'infoscout.pricescout.envsettings.prod'
    env.apache_conf = 'infoscout-prod'
    
    
def prod_api():
    prod()
    env.hosts = ['prod@184.169.145.240']
    
def prod_upload():
    prod()
    env.celeryd_conf = env.project_root + '/celeryd/config_prod'
    env.hosts = ['prod@184.169.148.63']
    
    
# Apps under south migration
south_apps = ('dynsettings', 
              'mobileauth', 
              'pricescoutapp', 
              'rdl',
              'mturk', 
              'gameengine', 
              'sentry', 
              'djcelery')

def deploy(codeonly=False, syncdb=True, staticfiles=True):
    """ Deploys to prod/staging environment """
      
    git_pull()
    
    if not codeonly:
    
        set_permissions()
            
        pip_install_req()
        
        validate()
    
        if staticfiles:
            collect_static()
    
        if syncdb:
            remote_syncdb()
    
        sync_dynsettings()
        
        # set them again, required for new logs files
        set_permissions()
        
    # Restart  celery
    if hasattr(env, 'celeryd_conf'):
        celeryd('restart')
    
    apache("restart")


#def prod_deploy():
#    """
#    jbrelig: Did not work well. Needs some work
#    """
#    
#    prod()
#    
#    # First roll out to prod_api
#    with settings(hosts=['prod@184.169.145.240'], ):
##        prod_api()
#        deploy()
#    
#    # Now roll out prod_upload 
#    #   Don't include the remote_syncdb 
#    #   and collect_static. Do that on the prod_api box
#    with settings(hosts=['prod@184.169.148.63']):
##        prod_upload()
#        git_pull()
#        set_permissions()
#        pip_install_req()
#        validate()
#        set_permissions()
#        celeryd('restart')
#        apache('restart')


def tag():
    """ Tags code to version number """
    
    local('git fetch --tags')
    print("Showing latest tags for reference")
    local('git tag | tail -5')
    refspec = prompt('Tag name [in format x.x.x]? ')
    local('git tag -a %(ref)s -m "Tagging version %(ref)s in fabfile"' % {
        'ref': refspec})
    local('git push --tags')    


def virtualenv(command):
    """ Wrap call in virtualenv """
    with cd(env.project_root):
        return sudo(env.activate + '&&' + command, user=env.deploy_user)


def collect_static():
    """ Collects static files for prod deploys """
    managepy("collectstatic --noinput")

def pip_install_req():
    with cd(env.project_root):
        virtualenv('pip install -r requirements.txt')


def remote_syncdb():
    """ Sync db remotely. """
    managepy("syncdb")
    managepy("migrate")


def _remote_syncdb_app(app):
    managepy("migrate "+app)


def local_syncdb():
    for app in south_apps:
        _local_syncdb_app(app)


def _local_syncdb_app(app):
    """ Sync db locally (creates schemamigration files) """
    
    with settings(warn_only=True):
        result = local("python manage.py schemamigration " + app + " --auto")
    if result.failed:
        pass
#        abort("Aborting at user request.")        
    
    local('python manage.py migrate ' + app)


def git_pull():
    
    local('git fetch --tags')
    
    local('git tag | tail -5')
    tag = fabric.operations.prompt("Tag to deploy? (blank for HEAD)")
    
    # If no tag provided, reset to branch
    if not tag:
        branch = fabric.operations.prompt("Branch to deploy? (blank for master)") or 'master'
        tag = "remotes/origin/%s" % branch 
        tag_name = local('git rev-parse %s' % tag, capture=True).strip()
    else:
        tag_name = tag

    with cd(env.source_root):
        run('git fetch --tags')
        run("git clean -f")
        run("git fetch")
        run("git reset --hard %s" % tag)
        
        # Write tag number to tag file
        run("echo %s > %s/tag" % (tag_name, env.project_root))


def validate():
    """ Validate nothing is broke """
    managepy("validate")
    
def set_permissions():
    with cd(env.project_root):
        sudo("chgrp www-data logs -R")
        sudo("chmod 775 logs -R")
        sudo("chmod 775 media")
        sudo("chmod 775 celeryd")


def sync_dynsettings():
    """ Sync dyn settings in database """
    managepy("syncsettings")
    
def setup_instance():
    """
    Installs base libraries on empty ec2 ubuntu environment. 
    
    We ideally should NOT have to run this again as 
    we have a snapshot of the ubuntu instance on AWS all loaded 
    and ready to go
    """
    
    sudo("apt-get install git")
    sudo("apt-get install htop")
    sudo("apt-get install apache2 libapache2-mod-wsgi")
    sudo("a2enmod mod-wsgi")
    sudo("apt-get install mysql-client python2.7-mysqldb")
    sudo("apt-get install memcached")
    sudo("apt-get install python-pip python-virtualenv python-dev build-essential")
    sudo("apt-get install python-imaging")
    sudo("apt-get install libxslt-dev libxml2-dev")
    
    # Uninstall some pacakges not using (or we dont want at OS)
    sudo("apt-get uninstall boto")
    
    # setup tesseract 3.0
    setup_tesseract()
    
    # setup open cv
    setup_opencv()
    
    # Removes 'indexes' on default apache vhost (security)
    sudo("perl -pi -e 's/Indexes//g' /etc/apache2/sites-available/default")
    apache("reload")
    
    
def setup_tesseract():
    """
    Have to install tesseract 3.00 from source. Used steps from here:
    http://dudczak.info/dry/index.php/2011/01/tesseract-3-0-installation-on-ubuntu-10-10-server/
    """

    sudo ("apt-get install build-essential autoconf")
    sudo ("apt-get install libpng12-dev libjpeg62-dev libtiff4-dev zlib1g-dev")
    sudo ("apt-get install libleptonica-dev")
    
    # Install leptonica from source (ignore, installed via aptitude above)
#    sudo ("mkdir /home/prod/leptonica")
#    with cd("/home/prod/leptonica"):
#        sudo("wget http://www.leptonica.org/source/leptonica-1.68.tar.gz")
#        sudo("tar -zxvf leptonlib-1.68.tar.gz")
#    with cd("/home/prod/leptonlib-1.68"):
#        sudo ("./configure")
#        sudo ("make")
#        sudo ("checkinstall")
#        sudo ("ldconfig")

    # Install tesseract from source
    sudo ("mkdir /home/ubuntu/tesseract")
    with cd("/home/ubuntu/tesseract"):
        sudo ("wget http://tesseract-ocr.googlecode.com/files/tesseract-3.00.tar.gz")
        sudo ("tar -zxvf tesseract-3.00.tar.gz")
    with cd("/home/ubuntu/tesseract/tesseract-3.00"):
        sudo ("./runautoconf")
        sudo ("./configure")
        sudo ("make")
        sudo ("make install")
        sudo ("ldconfig")
        
    # Install tesseract english language files
    with cd("/usr/local/share/tessdata"):
        sudo ("wget http://tesseract-ocr.googlecode.com/files/eng.traineddata.gz")
        sudo ("gunzip eng.traineddata.gz")
    
    
def setup_opencv():
    """
    Installs OpenCV with python bindings
    
    Documented on readme file here:
    https://github.com/brelig/infoscout/tree/master/infoscout/apps/rdl/bannerdetect
    """
    
    sudo ("apt-get install build-essential libgtk2.0-dev libjpeg62-dev libtiff4-dev libjasper-dev libopenexr-dev cmake python-dev")
    sudo ("apt-get install python-numpy libtbb-dev libeigen2-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev")
    sudo ("apt-get install libvorbis-dev libxvidcore-dev cmake-gui")
    
    sudo ("mkdir /home/ubuntu/opencv")
    with cd("/home/ubuntu/opencv"):
        sudo ("wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.3.1/OpenCV-2.3.1a.tar.bz2/download -O OpenCV-2.3.1a.tar.bz2")
        sudo ("tar -xvf OpenCV-2.3.1a.tar.bz2")
    with cd("/home/ubuntu/opencv/OpenCV-2.3.1"):
        sudo ("mkdir release")
    with cd ("/home/ubuntu/opencv/OpenCV-2.3.1/release"):
        sudo ("cmake -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=OFF -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON ..")
        sudo ("make")
        sudo ("make install")
       

def setup_environment():
    """
    Setups a new environment. Creates dir, clones git repo,
    installs virtualenv, etc.
    """
  
    # Copy SSH keypair for GitHub from root to deploy_user .ssh dir
    # NOTE: SSH keypair must already be in root dir. They should be
    with settings(warn_only=True):
        sudo("cp /root/.ssh/id_rsa* /home/%s/.ssh/." % env.deploy_user)
        sudo("chown -R %s:%s /home/%s/.ssh" % (env.deploy_user, env.deploy_user, env.deploy_user))
  
    # Create directory
    sudo("mkdir -p " + env.source_root)
    sudo("chown -R %s:%s %s" % (env.deploy_user, 'www-data', env.source_root))
    with cd(env.source_root):
        branch = env.branch if hasattr(env,'branch') else 'master'
        run("git clone -b %s %s ." % (branch, env.git_repo))
    sudo("chown -R %s:%s %s" % (env.deploy_user, 'www-data', env.source_root))
    
    # Install virtualenv and install pip reqs
    with cd(env.project_root):
        run("virtualenv ve")
    pip_install_req()
    
    # Link apache vhost 
    setup_apache_vhost(env.project_root, env.apache_conf)
    
    # Setup other apache vhosts
    if hasattr(env,'other_apache_confs'):
        for path, apache_conf in env.other_apache_confs:
            setup_apache_vhost(path, apache_conf)
    
def setup_apache_vhost(path, apache_conf):
    """ Creates sym link and activates apache conf """
    
    with settings(warn_only=True):
        sudo("rm /etc/apache2/sites-available/%s" % apache_conf)
    sudo("ln -s %s/apache/conf/%s /etc/apache2/sites-available/%s" % (path, apache_conf, apache_conf))
    sudo("a2ensite %s" % apache_conf)
    apache("reload")
    
    
    
    
#def server_install():
#    """
#    Deprecated... see setup_environment above
#    """
#    sudo('yum install -y git-core')
#    sudo('yum install -y httpd')
#    sudo('yum install -y httpd-devel')
#    sudo('yum install -y make')
#    sudo('yum install -y gcc')
#    sudo('yum install -y python-devel')
#    sudo('yum install -y mysql') 
#    sudo('yum install -y mysql-server') 
#    sudo('yum install -y mysql-devel') 
#    sudo('chgrp -R mysql /var/lib/mysql') 
#    sudo('chmod -R 770 /var/lib/mysql') 
#    install_mod_wsgi()
#    install_python_deps()
#
#    
#def install_mod_wsgi():
#    sudo('wget http://modwsgi.googlecode.com/files/mod_wsgi-3.3.tar.gz;tar -xzvf mod_wsgi-3.3.tar.gz;cd mod_wsgi-3.3; ./configure ; make ; make install;')
#
#
#def install_python_deps():
#    sudo('easy_install pip')
#    sudo('easy_install virtualenv')    


def init_datamaster_db():
    """ Creates datamaster tables """
    managepy("syncdb --database=datamaster")
    managepy('migrate datamaster --database="datamaster"')
    
def migrate_datamaster_db():
    managepy("migrate datamaster --database=datmaster")


def seedmasterdata(dataset="all"):
    """ Sync datamaster in database """
    managepy("seedmasterdata %s" % dataset)    
    
    
def seedbannerimages():
    """ Pull in banner images in database """
    managepy("seedbannerimages")
    apache('restart')
       
       
def synconionconfig():
    """ Pulls in config from s3. NOT using atm """
    managepy("synconionconfig")
         
         
def managepy(cmd):
    """ Run generic manage.py command """
    virtualenv("python manage.py %s --settings=%s" % (cmd, env.settings_module))
         
        
def last_commit():
    """ Simply outpus the last GIT commit deployed """
    with cd(env.project_root):
        run('git log -1 --format="%H%n%aD"')


def apache(cmd):
    sudo("/etc/init.d/apache2 " + cmd)


def memcache(cmd):
    sudo("/etc/init.d/memcached " + cmd)


def celeryd(cmd):
    """ Runs celeryd command. Example fab dev celeryd:start """
    sudo("%s/celeryd/celeryd %s %s" % (env.project_root, cmd, env.celeryd_conf))
    
    
def datadump(dumpmethod,local_file):
    """ 
    Runs datadump on specificed server and 
    downloads generated file to current directory
    """
    
    # Run command, the last line is the filename (slightly hacky)
    file_path = virtualenv('python manage.py datadump %s --settings=%s' % (dumpmethod, env.settings_module))
    file_path = file_path.strip()
    
    # Right now just saves to log dir (might be better spot?)
    print "Download dump file to %s" % local_file
    
    # Download file
    get(file_path, local_file)

    # Delete remote file
    sudo("rm %s" % file_path)