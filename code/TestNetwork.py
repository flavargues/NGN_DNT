#docker run --label "com.docker-tc.limit=1mbps" --label "com.docker-tc.delay=100ms" --label "com.docker-tc.loss=50%" --label "com.docker-tc.duplicate=50%" -it abbey22/traffic-control
from docker import *
from docker.errors import *
import time
import re

class TestNetwork():
	def __init__(self):
		self.containerList = []
		self.networkList = []

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
			print(f"NOT connected to docker daemon at {dockerDaemon}.")
			print("You can use docker-in-docker with docker-compose up -d and enter the IP address:2376 of the container.")

	def destroy(self):
		for it in self.containerList:
			try:
				it.remove(force=True)
			except Exception as error:
				pass
		self.dockerDaemon.networks.prune()
		self.containerList = []
		self.networkList = []
		#if len(self.containerList):
		#	for i in range(10):
		#		détruire container host{i}

	def build(self, topology: str, NumberOfContainers: int):
		topology = topology.lower()
		if topology not in ['star', 'fully connected'] or NumberOfContainers < 0 or NumberOfContainers > 10:
			raise Exception("Bad arguments.", topology, NumberOfContainers)
		if len(self.containerList) > 0:
			self.destroy()
		

		if topology == "fully connected":
			for i in range(NumberOfContainers):
				try:
					newContainer = self.dockerDaemon.containers.create("alpineping", command="/bin/sh",
						tty=True, detach=True, cap_add=["NET_ADMIN"], name=f"host{i}")
						
					self.containerList.append(newContainer)
					newContainer.start()
				except Exception as error:
					self.destroy()
					raise

		elif topology == "star":
			for i in range(NumberOfContainers):
				try:
					if i == 0:
						for j in range(1, NumberOfContainers):
							self.networkList.append(self.dockerDaemon.networks.create(f"b0-{j}"))

						newContainer = self.dockerDaemon.containers.create("alpineping", command="/bin/sh",
							tty=True, detach=True, cap_add=["NET_ADMIN"] , name="host0")
						self.containerList.append(newContainer)

						for it in self.networkList:
							it.connect("host0")
						
					else:
						newContainer = self.dockerDaemon.containers.create("alpineping", command="/bin/sh",
							tty=True, detach=True, cap_add=["NET_ADMIN"], name=f"host{i}", network=f"b0-{i}")
						self.containerList.append(newContainer)
						
					newContainer.start()
					time.sleep(1)

				except Exception as error:
					self.destroy()
					raise
			time.sleep(2)

			gateways = dict()
			center = self.containerList[0]
			center.reload()
			for network in self.networkList:
				network.reload()
				gateways[network.name] = center.attrs['NetworkSettings']['Networks'][network.name]['IPAddress']
			for edge in self.containerList[1:]:
				edge.reload()
				myNetwork = list(edge.attrs['NetworkSettings']['Networks'])[0]
				myGateway = gateways[myNetwork]
				output = edge.exec_run(f"ip route del default;	ip route add default via {myGateway}", tty=True)

			"""gateways = dict()
			for it in self.containerList:
				it.reload()
			for it in self.containerList:
				if it.name == "host0":
					networks = list(it.attrs['NetworkSettings']['Networks'].keys())
					for key in networks:
						gateways[key] = it.attrs['NetworkSettings']['Networks'][str(key)]['IPAddress']
				elif it.name != "host0":
					myGateway = gateways.index(str(list(	it.attrs['NetworkSettings']['Networks'].keys() )[0]   ))
					myGateway = gateways[str(list(it.attrs['NetworkSettings']['Networks'].keys())[0])]
					it.exec_run(f"ip route del default; ip route add default via {myGateway}")"""
		#add host names
		hostsFile = ""
		for it in self.containerList:
			it.reload()
			itOneNetwork = it.attrs['NetworkSettings']['Networks'].keys()[0]
			itIP = it.attrs['NetworkSettings']['Networks'][itOneNetwork]["IPAddress"]
			hostsFile += itIP + " " + it.name[1:] + "{}".format("\n")
		for it in self.containerList:
			it.exec_run("echo " + hostsFile + " >> /etc/hosts")
		
		
	#def getIPAddr(self):
	#	ipList = dict()
	#	for it in self.containerList:
	#		it.reload()
	#		ipList[it.attrs['Name']] = it.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
	#	return ipList
	#def generateHostsFileString(self, hostsIP):
	#	append = ""
	#	for it in self.containerList:
	#		name = it.attrs['Name']
	#		ip = hostsIP[name]
	#		append += ip + " " + name[1:] + "{}".format("\n")
	#	return append

	def ping(self, sender:str, receiver:str, duration:int = 5):
		feedback = self.dockerDaemon.containers.get(sender).exec_run("ping -Aq -c 1000 " + receiver, tty=True)
		
		count = feedback.count
		exit_code = feedback.exit_code
		index = feedback.index
		
		output = str(feedback.output)
		pt = re.search("(\d{1,}) pa", output)
		pr = re.search("(\d{1,}) r", output)
		rtt = re.search("(\d{1,})ms", output)

		temp = re.search("mdev(.{1,}),", output)
		min = re.findall("\d{1,}.\d{1,}", temp)[0]
		avg = re.findall("\d{1,}.\d{1,}", temp)[1]
		max = re.findall("\d{1,}.\d{1,}", temp)[2]
		mdev = re.findall("\d{1,}.\d{1,}", temp)[3]

		ipg = re.search("ewma (\d{1,}.\d{1,})", output)
		ewma = re.search("\/(\d{1,}.\d{1,}) ms\\r", output)

		return count, exit_code, index, pt, pr, rtt , temp, min, avg, max, mdev, ipg, ewma


"""
for twamp
	add file for the github
	compile them
for ping
	apk get install iputils
for bandwidth
	apt get install iftops
OWAMP ?
	???

"""