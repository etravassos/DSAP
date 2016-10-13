from logging import Filter
from src.core.utils import constants as const

class RespFilter(Filter):
    def filter(self, record):
        return record.levelno != const.LOGGING.RESP_STREAM_LEVEL

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'respfilter': {
            '()': RespFilter,
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(thread)d] [%(filename)18s:%(lineno)4s] [%(asctime)s - %(levelname)9s]: %(message)s'
        },
        'simple': {
            'format': '[%(thread)d] [%(module)s - %(funcName)s()] [%(levelname)s]: %(message)s'
        },
        'responsef': { 
            'format': '%(message)s' 
        }, 
    },
    'handlers': {
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['respfilter'],
        },
        'file': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'formatter':'verbose',
            'filename': '/var/log/dsap.log',
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
            'filters': ['respfilter'],
        },
        'resp': { 
            'level':'RESP', 
            'class':'src.logging.ResponseHandler.ResponseHandler', 
            'formatter': 'responsef',
        },
    },
    'loggers': {
        'ca.ciralabs.dsap': {
            'handlers':['console', 'file', 'resp'],
            'propagate': False,
            'level':'DEBUG',
        },
    }
}

def get_log_settings_dict():
    return LOGGING