from docker import *

class TestNetwork():
#init
	def __init__(self):
		self.containerList = []
		self.dockerDaemon = DockerClient

#main
	def connect(self, dockerDaemon):
		try:
			newDaemon = DockerClient(base_url=dockerDaemon)
			if newDaemon.ping():
				print("Connected to docker daemon.")
			else:
				raise Exception("Daemon doesn't ping back.")
			self.dockerDaemon = newDaemon

		except Exception as error:
			print("An exception occured !", error)
			print("You can use docker-in-docker with docker-compose up -d and enter the IP address:2376 of the container.")

	#def serverHealthCheck(self):
	#	try:
	#		if self.dockerDaemon.ping():
	#			print("Daemon healthy.")
	#	except Exception as error:
	#		print("Daemon error ! Detaching. Please connect().", error)
	#		self.dockerDaemon = None
	
	def start(self):
		for it in reversed(self.containerList):
			it.start()


	def destroy(self):
		for it in self.containerList:
			it.remove(force=True)

	def build(self, topology: str, NContainers: int):
	#arguments check
		topology = topology.lower()
		valid = {'star', 'chain', 'tree', 'ring', 'fully connected'}
		if topology not in valid:
			print("Topology unknown. Available values are : ['star', 'chain', 'tree', 'ring', 'fully connected'] (Non-case sensitive)")
			return
		if type(NContainers) != int or NContainers < 2:
			print("Incorrect number of containers. Must be <= 2.")
			return

		#TODO check if containerlist empty

		if   topology == 'star':
			try:
			#docker pull openvswitch/ovs:2.12.0_debian
			
			#create hosts at 0...NContainers - 1
				for i in range(1, NContainers):
					newHost = self.dockerDaemon.containers.create("alpine", command="/bin/sh", tty=True, detach=True,
					name="host{}".format(i)
					)
					self.containerList.append(newHost)
			#create switch at 0
				linkDict = dict()
				for i in range(1, NContainers):
					linkDict["host{}".format(i)] = "host{}".format(i)
					
				switch = self.dockerDaemon.containers.create("globocom/openvswitch", detach=True,
				name="switch", links=linkDict, tty=True, cap_add = ['NET_ADMIN'], stdin_open = True
				)
				self.containerList.insert(0, switch)

			except Exception as error:
				print("Error during network building ! Destroying containers.", error)
				self.destroy()

		elif topology == 'chain':
			pass
		elif topology == 'tree':
			pass
		elif topology == 'ring':
			pass
		elif topology == 'fully connected':
			pass

		#			LinkingList[i][i + 1] = 1
		#		for i in range(NContainers - 1):
		#		LinkingList[0][range(NContainers)] = 1
		#		LinkingList[range(NContainers)][range(NContainers)] = 1
		#for i in range(NContainers):
		#try:
		#	for i in range(NContainers):
		#		n = self.dockerDaemon.containers.create('alpine')
		#		self.containerList.append(n)
		#except docker.errors.ImageNotFound as error:
		#	self.dockerDaemon.images.pull
		#LinkingList = [[0 for col in range(NContainers)] for row in range(NContainers)]




	
#helper functions