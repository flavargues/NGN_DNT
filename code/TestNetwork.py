from docker import *
from docker.errors import *
import time
import re

class TestNetwork():
	def __init__(self):
		self.containerList = []

#main
	def connect(self, dockerDaemon = 'unix:///var/run/docker.sock'):
		try:
			newDaemon = DockerClient(base_url=dockerDaemon)
			if newDaemon.ping():
				print("Connected to docker daemon.")
				self.dockerDaemon = newDaemon
			else:
				raise Exception("Daemon doesn't ping back.")
		except Exception:
			print("You can use docker-in-docker with docker-compose up -d and enter the IP address:2376 of the container.")
			raise

	def destroy(self):
		for it in self.containerList:
			try:
				it.remove(force=True)
				self.containerList.pop(0)
			except Exception as error:
				pass

	def build(self, topology: str, NContainers: int):
	#arguments check
		topology = topology.lower()
		if topology not in ['star', 'tree', 'ring', 'fully connected'] or NContainers < 0 or NContainers > 10:
			raise Exception("Bad arguments", topology, NContainers)
	#empty containerList
		if len(self.containerList) > 0:
			self.destroy()
		
	#building topology
		if   topology == 'star':
			try:
			#create hosts at 0...NContainers - 1
				for i in range(NContainers):
					newContainer = self.dockerDaemon.containers.create("alpine", command="/bin/sh", tty=True, detach=True,
					name="host{}".format(i)
					)
					self.containerList.append(newContainer)
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
			for i in range(NContainers):
				try:
					containerName = "host{}".format(i)
					if i == 0:
						newContainer = self.dockerDaemon.containers.create("alpine", "/bin/sh", detach=True, name=containerName,
						stdin_open = True)
						newContainer.start()
					else:
						link = dict()
						newContainer = self.dockerDaemon.containers.create("alpine", "/bin/sh", detach=True, name=containerName,
						links = dict([(previousName, previousName)]), stdin_open = True)
						newContainer.start()
					self.containerList.append(newContainer)
					previousName = containerName
					
				except Exception as error:
					raise
			
		elif topology == 'tree':
			pass
		elif topology == 'ring':
			pass
		elif topology == 'fully connected':
			for i in range(NContainers):
				try:
					newContainer = self.dockerDaemon.containers.create("alpineping", command="/bin/sh",
						tty=True, detach=True, name="host{}".format(i))
					self.containerList.append(newContainer)
					newContainer.start()
				except Exception as error:
					self.destroy()
					raise

		time.sleep(3)
		self.hostsString=self._generateHostsFileString(self._getIPAddr())
		for it in self.containerList:
			it.exec_run("ash -c \"echo -e "+"\'" + self.hostsString + "\'" +" >> /temp.txt\"")
			it.exec_run("ash -c \"cat /temp.txt" + " >> /etc/hosts\"")

	def _getIPAddr(self):
		ipList = dict()
		for it in self.containerList:
			it.reload()
			ipList[it.attrs['Name']] = it.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
		return ipList

	def _generateHostsFileString(self, hostsIP):
		append = ""
		for it in self.containerList:
			name = it.attrs['Name']
			ip = hostsIP[name]
			append += ip + " " + name[1:] + "{}".format("\n")
		return append

	def ping(self, sender:str, receiver:str, duration:int = 5):
		feedback = self.dockerDaemon.containers.get(sender).exec_run("ping -Aq -c 1000 " + receiver, tty=True)
		
		count = feedback.count
		exit_code = feedback.exit_code
		index = feedback.index
		
		output = str(feedback.output)
		pt = re.search("(\d{1,}) pa", output)
		pr = re.search("(\d{1,}) r", output)
		RTT = re.search("(\d{1,})ms", output)

		temp = re.search("mdev(.{1,}),", output)
		min = re.findall("\d{1,}.\d{1,}", temp)[0]
		avg = re.findall("\d{1,}.\d{1,}", temp)[1]
		max = re.findall("\d{1,}.\d{1,}", temp)[2]
		mdev = re.findall("\d{1,}.\d{1,}", temp)[3]

		ipg = re.search("ewma (\d{1,}.\d{1,})", output)
		ewma = re.search("\/(\d{1,}.\d{1,}) ms\\r", output)

		return count, exit_code, index, pt, pr, RTT, temp, min, avg, max, mdev, ipg, ewma


d run --label "com.docker-tc.limit=1mbps" --label "com.docker-tc.delay=100ms" --label "com.docker-tc.loss=50%" --label "com.docker-tc.duplicate=50%" -it abbey22/traffic-control