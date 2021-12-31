#docker run --label "com.docker-tc.limit=1mbps" --label "com.docker-tc.delay=100ms" --label "com.docker-tc.loss=50%" --label "com.docker-tc.duplicate=50%" -it abbey22/traffic-control
from docker import *
from docker.errors import *
import time

class TestNetworkConfiguration():
	"""
	Example:

		>>> configuration = TestNetworkConfiguration(
				topology="star",
				names=    ["host0", "host1", "host2", "host3"],
				throttled=["True" ,"True"  ,"True"  ,"True"  ],
				bandwidth=["1mbps","1mbps" ,"1mbps" ,"1mbps" ],
				delay=    ["100ms","100ms" ,"100ms" ,"100ms" ],
				loss=     ["50%"  ,"50%"   ,"50%"   ,"50%"   ],
				duplicate=["0%"   ,"0%"    ,"0%"    ,"0%"    ],
				corrupt=  ["0%"   ,"0%"    ,"0%"    ,"0%"    ]
			)
	"""
	def __init__(self, topology:str="full", names=None, numberOfNodes:int=None, throttled:list=None, bandwidth:list=None, delay:list=None,
	loss:list=None, duplicate:list=None, corrupt:list=None):
		self._params=dict()

		if topology.lower() in ["full", "star"]:
			self.topology=topology.lower()
		else:
			raise ValueError(f"Bad topology={str(topology)}.")

		if type(names) == list and len(names) > 3 and len(names) < 10:
			self._params = {me: dict() for me in names}
		else:
			if type(numberOfNodes) == int and numberOfNodes > 3 and numberOfNodes < 10:
				self._params = {f"host{i}": dict() for i in range(numberOfNodes)}
			else:
				raise ValueError(f"Bad names={str(names)} 3<list<10 or numberOfNodes={str(numberOfNodes)} 3<x<10.")

		for i in range(len(self._params)):
			myParams = dict([
				("enabled",   bool(throttled[i] == "True"), ),
				("bandwidth", str(bandwidth[i]),            ),
				("delay",     str(delay[i]),                ),
				("loss",      int(loss[i].strip("%")),      ),
				("duplicate", int(duplicate[i].strip("%"))  ),
				("corrupt",   int(corrupt[i].strip("%"))    )
			])
			self._params[str(list(self._params.keys())[i])] = myParams

			

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

	def build(self, networkConfig: TestNetworkConfiguration):
		"""docker network create test-net
		docker run -it \
			--net test-net \
			--label "com.docker-tc.enabled=1" \
			--label "com.docker-tc.limit=1mbps" \
			--label "com.docker-tc.delay=100ms" \
			--label "com.docker-tc.loss=50%" \
			--label "com.docker-tc.duplicate=50%" \
			--label "com.docker-tc.corrupt=10%" \
			busybox \
			ping google.com"""

		topology = networkConfig.topology
		#better destroy
		if len(self.containerList) > 0:
			self.destroy()
		

		if topology == "full":
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
				#if network.name == "bridge":
				#	continue
				gateways[network.name] = center.attrs['NetworkSettings']['Networks'][network.name]['IPAddress']
				
			output = list()
			for edge in self.containerList[1:]:
				edge.reload()
				myNetwork = list(edge.attrs['NetworkSettings']['Networks'])[0]
				myGateway = gateways[myNetwork]
				command = f"ip route add default via {myGateway}"
				output.append( edge.exec_run("ip route del default", tty=True) )
				time.sleep(0.5)
				output.append( edge.exec_run(f"ip route add default via {myGateway}", tty=True) )
		
		#build IP table
		self.IPTable = {}
		for it in self.containerList:
			it.reload()
			itOneNetwork = list(it.attrs['NetworkSettings']['Networks'].keys())[0]
			itIP = it.attrs['NetworkSettings']['Networks'][itOneNetwork]["IPAddress"]
			self.IPTable[ str(it.name) ] = ( str(itIP) )

		
		
		
	def _resolve(self, name: str):
		if name in self.IPTable:
			return self.IPTable[name]
		else:
			raise KeyError(name)


	def ping(self, sender:str, receiver:str, duration:int = 5):

		out = self.dockerDaemon.containers.get(sender).exec_run("traceroute " + self._resolve(receiver), tty=True)
		
		#feedback = dict()
		#feedback['count'] = out.count
		#feedback['exit_code'] = out.exit_code
		#feedback['index'] = out.index
		#output = str(feedback.output)
		#feedback['output'] = output
		#feedback['pt'] = re.search("(\d{1,}) pa", out)
		#feedback['pr'] = re.search("(\d{1,}) r", out)
		#feedback['rtt'] = re.search("(\d{1,})ms", out)
		#temp = re.search("mdev(.{1,}),", out)
		#feedback['min'] = re.findall("\d{1,}.\d{1,}", temp)[0]
		#feedback['avg'] = re.findall("\d{1,}.\d{1,}", temp)[1]
		#feedback['max'] = re.findall("\d{1,}.\d{1,}", temp)[2]
		#feedback['mdev'] = re.findall("\d{1,}.\d{1,}", temp)[3]
		#feedback['ipg'] = re.search("ewma (\d{1,}.\d{1,})", out)
		#feedback['ewma'] = re.search("\/(\d{1,}.\d{1,}) ms\\r", out)

		return out


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