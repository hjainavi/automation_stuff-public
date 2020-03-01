import logging.config
import ssl

syslog_host = 'DUROTAN.FROSTWOLFS.ORG'
syslog_port = 6514
syslog_cert_path = '/root/CA.pem'
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s django %(name)s: %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'syslog': {
            'level': 'INFO',
            'class': 'tlssyslog.handlers.TLSSysLogHandler',
            'formatter': 'simple',
            'address': (syslog_host, syslog_port),
            'ssl_kwargs': {
                'cert_reqs': ssl.CERT_REQUIRED,
                'ssl_version': ssl.PROTOCOL_TLSv1_2,
                'ca_certs': syslog_cert_path,
            },
        },
    },
    'root': {
        'handlers': ['syslog'],
        'level': 'INFO',
    }
})

logger = logging.getLogger()
logger.error("AVI ROCKS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ****************************")
import time; time.sleep(2)
