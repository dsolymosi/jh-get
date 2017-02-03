
import os
import sys


c.JupyterHub.services = [
    {
        'name': 'jh-get',
        'url': 'http://127.0.0.1:10148',
        'command': [sys.executable, './jh-get.py'],
        'environment': {
        	#The path to user folders, where their notebooks are stored.
        	#You can use {user} which will be replaced by the user's name, eg. '/home/{user}'
        	'JUPYTERHUB_USER_PATH': '/home/{user}',

        }
    }
]