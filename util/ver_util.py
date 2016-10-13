import os
print ("Current execution dir: ", os.getcwd(), "\n")

try:
    import platform
    print ("Python:  " + platform.python_version())
except ImportError:
    print ("Somehow you are running this without Python")
   
try:
    import dns.version
    print ("\t DnsPython: ", dns.version.version)
except ImportError:
    print ("!Could not import DnsPython!")

try:
    import eppy
    print ("\t EPP: ", eppy.__version__)
except ImportError:
    print ("!Could not import EPP!")
   
try:
    import backports.ssl_match_hostname
    print ("\t backports.ssl_match_hostname: ", backports.ssl_match_hostname.__version__)
except ImportError:
    print ("!Could not import backports.ssl_match_hostname!")
   
try:
    import django
    print ("\t Django: ", django.__version__)
except ImportError:
    print ("!Could not import Django!")
   
try:
    import rest_framework
    print ("\t Django-REST-framework: ", rest_framework.__version__)
except ImportError:
    print ("!Could not import Django-REST-framework!")
   
try:
    import pip #package __version__ broken
    
    _v = [ pkg.version for pkg in pip.get_installed_distributions()
                if pkg.key in ['drf-nested-routers'] ]
    
    if len(_v) == 0:
        raise ImportError
    
    print ("\t drf-nested-routers: ", _v[0])
except ImportError:
    print ("!Could not import drf-nested-routers!")
    
try:
    import getdns
    print ("\t getdnsapi: ", getdns.__version__)
except ImportError:
    print ("!Could not import getdnsapi!")
    
try: 
   import psycopg2 
   print ("\t Psycopg2 (PostgreSQL): ", psycopg2.__version__) 
except ImportError: 
   print ("!Could not import Psycopg2 (PostgreSQL)!") 
   
try: 
   import mock
   print ("\t mock: ", mock.__version__) 
except ImportError: 
   print ("!Could not import mock!") 