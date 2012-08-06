#!/usr/bin/env python
from django.core.management import execute_manager
import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings
import os
import sys

PROJECT_ROOT = os.path.dirname(__file__)

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.insert(0, os.path.join(PROJECT_ROOT, "../.."))

# add app folder to python path
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../apps"))


if __name__ == "__main__":
    execute_manager(settings)
