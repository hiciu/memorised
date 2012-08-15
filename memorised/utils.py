"""memorised module - container for the memorise python-memcache decorator"""
__author__ = 'Wes Mason <wes [at] 1stvamp [dot] org>'
__docformat__ = 'restructuredtext en'
__version__ = '1.0.1'

import memcache
from hashlib import md5
import inspect

def uncache(fn, mc=None, mc_servers=None, parent_keys=[]):
        if not mc:
                if not mc_servers:
                        mc_servers = ['localhost:11211']
                mc = memcache.Client(mc_servers, debug=0)
        def wrapper(*args, **kwargs):
                argnames = fn.__code__.co_varnames[:fn.__code__.co_argcount]
                method = False
                static = False
                if hasattr(fn, 'im_self'):
                        method = True
                        if inspect.isclass(fn.__self__):
                                static = True

                arg_values_hash = []
                # Grab all the keyworded and non-keyworded arguements so
                # that we can use them in the hashed memcache key
                for i,v in (list(zip(argnames, args)) + list(kwargs.items())):
                        arg_values_hash.append("%s=%s" % (i,v))

                class_name = None
                if method:
                        keys = []
                        if len(parent_keys) > 0:
                                for key in parent_keys:
                                        keys.append("%s=%s" % (key, getattr(fn.__self__, key)))
                        keys = ','.join(keys)
                        # Get the class name from the self argument
                        if inspect.isclass(fn.__self__):
                                class_name = fn.__self__.__name__
                        else:
                                class_name = fn.__self__.__class__.__name__
                        module_name = inspect.getmodule(fn.__self__).__name__
                        parent_name = "%s.%s[%s]::" % (module_name, class_name, keys)
                else:
                        # Function passed in, use the module name as the
                        # parent
                        parent_name = inspect.getmodule(fn).__name__
                # Create a unique hash of the function/method call
                key = "%s%s(%s)" % (parent_name, fn.__name__, ",".join(arg_values_hash))
                key = md5(key.encode('utf-8')).hexdigest()

                if mc:
                        mc.delete(key)
                        return True
                else:
                        return False
        return wrapper
