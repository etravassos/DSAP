import logging
import logging.config
from inspect import currentframe
from os.path import normcase
from . import log_config
from src.core.utils import constants as const

def_logger='ca.ciralabs.dsap'
class Logger:

    """
    Class that implements a Singleton recipe in order to have one instance of the logging module.
    """
    class __Logger:
        _LOG = logging
        LOG = None

        def __init__(self, logger_set=def_logger):
            self.monkeypatch_findCaller()
            self.monkeypatch_resp_logging_level()
             
            self._LOG.config.dictConfig(log_config.get_log_settings_dict())
            self.LOG = self.get_logger(logger_set)
            self.monkeypatch_multilog()

        def switch_logger(self, logger_set):
            self.LOG = self._LOG.getLogger(logger_set)
            self.monkeypatch_multilog()

        def get_logger(self, logger_set):
            return self._LOG.getLogger(logger_set)
        
        def monkeypatch_multilog(self):
            self.LOG.multilog = self.multilog
            self.LOG.mul_dr = self.multilog_dr
            self.LOG.mul_wr = self.multilog_wr
        
        def multilog(self, streams, *messages):
            for stream in streams:
                getattr(self.LOG, stream)(*messages)
        
        def multilog_dr(self, *messages):
            self.multilog(("debug", "resp"), *messages)
            
        def multilog_wr(self, *messages):
            self.multilog(("warn", "resp"), *messages)
            
        @staticmethod 
        def monkeypatch_resp_logging_level(): 
            logging.RESP = const.LOGGING.RESP_STREAM_LEVEL 
            logging.addLevelName(logging.RESP, "RESP") 
            logging.Logger.resp = lambda inst, msg, *args, **kwargs: inst.log(logging.RESP, msg, *args, **kwargs) 
            logging.resp = lambda msg, *args, **kwargs: logging.log(logging.RESP, msg, *args, **kwargs) 
        
        @staticmethod
        def monkeypatch_findCaller():
            if __file__.lower()[-4:] in ['.pyc', '.pyo']:
                _wrapper_srcfile = __file__.lower()[:-4] + '.py'
            else:
                _wrapper_srcfile = __file__
            _wrapper_srcfile = normcase(_wrapper_srcfile)
            
            def findCaller(self, stack_info=False):
                """
                Find the stack frame of the caller so that we can note the source
                file name, line number and function name.
                """
                f = currentframe()
                #On some versions of IronPython, currentframe() returns None if
                #IronPython isn't run with -X:Frames.
                if f is not None:
                    f = f.f_back
                rv = "(unknown file)", 0, "(unknown function)", None
                while hasattr(f, "f_code"):
                    co = f.f_code
                    filename = normcase(co.co_filename)
                    if filename == _wrapper_srcfile or filename == logging._srcfile:
                        f = f.f_back
                        continue
                    sinfo = None
                    if stack_info:
                        sio = io.StringIO()
                        sio.write('Stack (most recent call last):\n')
                        traceback.print_stack(f, file=sio)
                        sinfo = sio.getvalue()
                        if sinfo[-1] == '\n':
                            sinfo = sinfo[:-1]
                        sio.close()
                    rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
                    break
                return rv
                    
            logging.Logger.findCaller = findCaller

    instance = None

    def __new__(cls,  logger_set=def_logger):
        if not Logger.instance:
            Logger.instance = Logger.__Logger(logger_set=def_logger)
        else:
            Logger.instance.switch_logger(logger_set=def_logger)
        return Logger.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)