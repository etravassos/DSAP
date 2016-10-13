from logging import Handler
import threading
from collections import defaultdict

class ResponseLogDict:
    """
    Class that implements a Singleton recipe in order to have one instance of the ResponseLogDict
    """
    class __ResponseLogDict:
        resp = defaultdict(list)

        def __init__(self):
            pass
        
        def append(self, record):
            self.resp[threading.get_ident()].append(record)
        
        def get_resp(self, clear):
            thr = threading.get_ident()
            r = self.resp[thr].copy()
            if clear:
                self.resp.pop(thr)
            return r
        
        def clear(self):
            self.resp.pop(threading.get_ident())

    instance = None

    def __new__(cls):
        if not ResponseLogDict.instance:
            ResponseLogDict.instance = ResponseLogDict.__ResponseLogDict()
        # else:
        #     ResponseLogDict.instance.switch_logger(logger_set=def_logger)
        return ResponseLogDict.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)
        
class ResponseHandler(Handler):
    rld = ResponseLogDict()
    
    def emit(self, record):
        log_entry = self.format(record)
        self.rld.append(log_entry)
        # return None
        
    