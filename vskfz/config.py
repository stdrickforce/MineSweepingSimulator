#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: stdrickforce (Tengyuan Fan)
# Email: <stdrickforce@gmail.com> <fantengyuan@baixing.com>


LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': True,
    'loggers': {
        'main': {
            'handlers': ['file'],
            'propagate': False,
            'level': 'INFO',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'general',
            'filename': '/Users/stdrickforce/mine.log',
        },
    },
    'formatters': {
        'general': {
            'format': '%(asctime)s %(levelname)-8s[%(name)s][%(process)d]'
            ' %(message)s',
        },
    },
}
