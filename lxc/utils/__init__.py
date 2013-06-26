import subprocess
import os

class ContainerAlreadyExists(Exception):
	def __init__(self, container_name):
		self.container_name = containter_name

	def __str__(self):
		return 'Container {} already exists!'.format(self.container_name)

class ContainerNotExists(Exception):
	def __init__(self, container_name):
		self.container_name = container_name

	def __str__(self):
		return 'Container {} not exists!'.format(self.container_name)

class ContainerIsAlreadyRunning(Exception):
	def __init__(self, container_name):
		self.container_name = container_name

	def __str__(self):
		return 'Container {} is already running!'.format(self.container_name)

class ContainerIsNotRunning(Exception):
	def __init__(self, container_name):
		self.container_name = container_name

	def __str__(self):
		return 'Container {} is not running!'.format(self.container_name)
		
class ContainerIsNotFrozen(Exception):
	def __init__(self, container_name):
		self.container_name = container_name

	def __str__(self):
		return 'Container {} is not frozen!'.format(self.container_name)

def start(container_name, config_file = None):
	'''
	Starts container with a given name
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	if get_state(container_name) == 'RUNNING':
		raise ContainerIsAlreadyRunning(container_name)

	cmd = ['lxc-start', '--name', container_name]
	if config_file != None:
		cmd.extend(['--rcfile', config_file])
	cmd.append('--daemon')
	return_value = subprocess.check_call(cmd)
	return return_value

def stop(container_name):
	'''
	Stops container with a given name
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	if get_state(container_name) == 'STOPPED':
		raise ContainerIsNotRunning

	cmd = ['lxc-stop', '--name', container_name]
	return_value = subprocess.check_call(cmd)
	return return_value

def shutdown(container_name, timeout = None):
	'''
	Softly stops container with a given name
	For much details see "lxc-shutdown -h"
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	if get_state(container_name) == 'STOPPED':
		raise ContainerIsNotRunning(container_name)

	cmd = ['lxc-shutdown', '--name', container_name, '--timeout', timeout]
	return_value = subprocess.check_call(cmd)
	return return_value

def create(container_name, config_file = None):
	'''
	Creates container with a given name and given config file
	'''
	if exists(container_name):
		raise ContainerAlreadyExists(container_name)

	cmd = ['lxc-create', '--name', container_name]
	if config_file != None:
		cmd.extend(['-f', config_file])
	return_value = subprocess.check_call(cmd)
	return return_value	

def destroy(container_name):
	'''
	Destroys container with a given name
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	if get_state(container_name) == 'RUNNING':
		raise ContainerIsAlreadyRunning(container_name)

	cmd = ['lxc-destroy', '--name', container_name]
	return_value = subprocess.check_call(cmd)
	return return_value

def freeze():
	'''
	Freezes container with a given name
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	if get_state(container_name) != 'RUNNING':
		raise ContainerIsNotRunning(container_name)

	cmd = ['lxc-freeze', '--name', container_name, '--quiet']
	return_value = subprocess.check_call(cmd)
	return return_value

def unfreeze():
	'''
	Unfreezes container with a given name
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	if get_state(container_name) != 'FROZEN':
		raise ContainerIsNotFreezed(container_name)

	cmd = ['lxc-unfreeze', '--name', container_name, '--quiet']
	return_value = subprocess.check_call(cmd)
	return return_value

def ls():
	'''
	Returns list of existing containers
	'''
	try:
		containers_list = os.listdir('/var/lib/lxc')
	except OSError:
		containers_list = []
	return sorted(containers_list)

def exists(container_name):
	'''
	Check if container exists
	'''
	if container_name in ls():
		return True
	else:
		return False

def info(container_name):
	'''
	Returns dictionary including following keys:
		- state
		- pid
	'''
	if not exists(container_name):
		raise ContainerNotExists(container_name)

	cmd = ['lxc-info', '--name', container_name, '--state', '--pid', '--quiet']
	output = subprocess.check_output(cmd, universal_newlines = True)
	info_dict = {
		'state': '',
		'pid': ''
	}
	info_dict['state'] = output.splitlines()[0].split()[1]
	info_dict['pid'] = int(output.splitlines()[1].split()[1])
	return info_dict

def get_state(container_name):
	'''
	Returns state of container with a given name
	'''
	return info(container_name)['state']

def list():
	'''
	Returns dictionary of lists
	For example
	{
		'running': ['a','b','c'],
		'stopped': ['d','e']
		'frozen': ['f']
	}
	'''
	stopped = []
	frozen = []
	running = []
	for container_name in ls():
		state = get_state(container_name)
		if state == 'RUNNING':
			running.append(container_name)
		elif state == 'STOPPED':
			stopped.append(container_name)
		elif state == 'FROZEN':
			frozen.append(container_name)
	return {
		'frozen': frozen,
		'running': running,
		'stopped': stopped
	}
