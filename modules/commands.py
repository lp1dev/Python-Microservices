
import logging as log
import config
available_commands = ["quit", "list", "start", "kill", "status", "restart", "clear", "keepalive", "log"]

def handle_input(command, worker, server=None):
  command = command.strip()
  command = command.split(" ")
  if command[0] not in available_commands:
    return False, help(worker, command)
  else:
    print(command)
    output = eval("%s" %command[0])(worker, command, server)
    return True, output

def log(worker, args=None, server=None):
  if "log_file" in config.daemon.keys():
    with open(config.daemon['log_file']) as f:
      return f.read()
  return "Unable to find logfile"
  
def keepalive(worker, args=None, server=None):
  if len(args) < 3:
    return "You must specify a value. Example : keepalive 1 true"
  id = int(args[1])
  service = worker.getService(id)
  if service is None:
    return "There isn't such service"
  service.keepAlive = bool(args[2])
  return args[2]
  
def restart(worker, args=None, server=None):
  worker.restart()
  return "Worker restarted"

def clear(worker, args=None, server=None):
  return "\033[H\033[2J"
  
def quit(worker, args=None, server=None):
  print("Quitting server")
  server.stop()                                                                                                                                              
  print("Closing running services...")                                                                                                                       
  for service in worker.services:
    service.stop()
  print("Goodbye !\n")
  exit(0)

def help(worker, args=None, server=None):
  command = args[0]
  return ("%s not in commands : %s" %(command, available_commands))

def status(worker, args=None, server=None):
  if len(args) > 1:
    id = int(args[1])
    service = worker.getService(id)
    if service is None:
      return "There isn't such service"
    return "[%i] | %s | Alive : %s" %(service.id, service.name, service.isAlive())
  return "Invalid number of arguments"

def list(worker, args=None, server=None):
  strlist = ""
  for service in worker.services:
    strlist += "[%i] | %s | Alive : %s | keepAlive : %s\n" %(service.id, service.name, service.isAlive(), service.keepAlive)
  return strlist

def start(worker, args=None, server=None):
    if len(args) > 1:
        id = int(args[1])
        service = worker.getService(id)
        if service is None:
          return "There isn't such service"
        if not service.isAlive():
            service.start()
            return "service started"
        else:
            log.warning("Service %i is already running" %id)
            return "Service is already running"
    return "Invalid number of arguments"
          
def kill(worker, args=None, server=None):
    if len(args) > 1:
        worker.kill(int(args[1]))
        return "Service killed"
    return "Cannot find service"

