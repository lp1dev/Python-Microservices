import config
import logging as log
from sys import exit

def check_config():
    mandatory_in_services = ["restart", "directory", "main_method"]
    try:
        for service_name in config.run.keys():
            service_conf = config.run[service_name]
            for mandatory in mandatory_in_services:
                if mandatory not in service_conf.keys():
                    log.error("Your service configuration must contain the attributes %s. %s is missing %s" %(mandatory_in_services, service_name, mandatory))
                    exit(-1)
        
    except AttributeError as e:
        log.error("Your config.py hasn't a correct format : [%s]" %str(e))
        exit(-1)

