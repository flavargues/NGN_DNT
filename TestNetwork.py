from docker import *
from docker.errors import *
from docker.types import Mount
import time
from progress.bar import Bar

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
	def len(self):
		return len(list(self._params.keys()))

	def names(self):
		return list(self._params.keys())

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
				("loss",      str(loss[i])                  ),
				("duplicate", str(duplicate[i])             ),
				("corrupt",   str(corrupt[i])               )
			])
			self._params[str(list(self._params.keys())[i])] = myParams
			self.__labels = 0

	def _labels(self):
		if self.__labels == 0:
			output = dict()
			for container in enumerate(self._params):
				thisContainer = dict()

				name = container[1]
				thisContainer['com.docker-tc.enabled'] = str(int((self._params[name]['enabled'])))
				thisContainer['com.docker-tc.limit'] = self._params[name]['bandwidth']
				thisContainer['com.docker-tc.delay'] = self._params[name]['delay']
				thisContainer['com.docker-tc.loss'] = self._params[name]['loss']
				thisContainer['com.docker-tc.duplicate'] = self._params[name]['duplicate']
				thisContainer['com.docker-tc.corrupt'] = self._params[name]['corrupt']
				thisContainer['edu.testNetwork.managed'] = "1"

				output[name] = thisContainer
			self.__labels = output
		return self.__labels
		

class TestNetwork():
	def __init__(self):
		self.containerList = []
		self.networkList = []
		self.trafficController = 0

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
				#self.containerList.remove(it)
				it.remove(force=True)
			except Exception:
				raise
		self.dockerDaemon.networks.prune()
		self.networkList = []
		self.containerList = []
		self.trafficController.remove(force=True)
		self.trafficController = 0
		if len(self.containerList) > 0:
			for unknownContainer in self.dockerDaemon.containers.list():
				try:
					unknownContainer.reload()
					if unknownContainer.attrs['Config']["Labels"]['edu.testNetwork.managed'] == "1":
						self.containerList.append(unknownContainer)
				except KeyError:
					continue
		
	def __ensureTrafficControl(self):		
		if self.trafficController == 0:
			
			mount1 = Mount(target="/var/run/docker.sock", source="/var/run/docker.sock")
			mount2 = Mount(target="/var/docker-tc", source="/var/docker-tc")

			mounts = list()
			mounts.append(mount1)
			mounts.append(mount2)
			
			self.trafficController = self.dockerDaemon.containers.create("lukaszlach/docker-tc",
			name="docker-tc", cap_add=["NET_ADMIN"], network="host",
			volumes={
				'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
				'/var/docker-tc': {'bind': '/var/docker-tc', 'mode': 'rw'}
			})
			self.trafficController.start()
			time.sleep(1)

	def build(self, networkConfig: TestNetworkConfiguration):
		bar = Bar('Starting Traffic Control', max=networkConfig.len() + 1)

		image = "flavargues/testerimage"
		command="/bin/sh"

		topology = networkConfig.topology
		#better destroy
		if len(self.containerList) > 0:
			self.destroy()

		self.__ensureTrafficControl()
		bar.next()
		bar.message = "creating containers"

		if topology == "full":
			for index, containerName in enumerate(networkConfig._params):

				try:
					myLabels = networkConfig._labels()[containerName]
					self.networkList.append(self.dockerDaemon.networks.create("test-net"))
					newContainer = self.dockerDaemon.containers.create(image=image, command=command,
						tty=True, detach=True, cap_add=["NET_ADMIN"], name=containerName, network="test-net",
						labels=myLabels)
					self.containerList.append(newContainer)
					newContainer.start()
				except Exception as error:
					self.destroy()
					raise
				bar.next()
		elif topology == "star":
			for index, containerName in enumerate(networkConfig._params):
				try:
					if index == 0:
						for j in range(1, networkConfig.len()):
							self.networkList.append(self.dockerDaemon.networks.create(f"b0-{j}"))

						newContainer = self.dockerDaemon.containers.create(image=image, command=command,
							tty=True, detach=True, cap_add=["NET_ADMIN"], name=containerName,
							labels=networkConfig._labels()[containerName])
						self.containerList.append(newContainer)

						for it in self.networkList:
							it.connect(networkConfig.names()[0])
						
					else:
						newContainer = self.dockerDaemon.containers.create(image=image, command=command,
							tty=True, detach=True, cap_add=["NET_ADMIN"], name=containerName,
							labels=networkConfig._labels()[containerName], network=f"b0-{index}")
						self.containerList.append(newContainer)
						
					newContainer.start()
					time.sleep(1)

				except Exception as error:
					self.destroy()
					raise
				bar.next()
			
			bar.message = "Preparing IP Table"
			gateways = dict()
			center = self.containerList[0]
			center.reload()
			for network in self.networkList:
				network.reload()
				#if network.name == "bridge":
				#	continue
				gateways[network.name] = center.attrs['NetworkSettings']['Networks'][network.name]['IPAddress']
			
			bar.message = "Configuring containers IP routing"
			output = list()
			for edge in self.containerList[1:]:
				edge.reload()
				myNetwork = list(edge.attrs['NetworkSettings']['Networks'])[0]
				myGateway = gateways[myNetwork]
				command = f"ip route add default via {myGateway}"
				output.append( edge.exec_run("ip route del default", tty=True) )
				time.sleep(0.5)
				output.append( edge.exec_run(f"ip route add default via {myGateway}", tty=True) )
			
		
		bar.message = "Building IP table"
		bar.next()
		self.IPTable = {}
		for it in self.containerList:
			it.reload()
			itOneNetwork = list(it.attrs['NetworkSettings']['Networks'].keys())[0]
			itIP = it.attrs['NetworkSettings']['Networks'][itOneNetwork]["IPAddress"]
			self.IPTable[ str(it.name) ] = ( str(itIP) )
		bar.finish()

	def __resolve(self, name: str):
		if name in self.IPTable:
			return self.IPTable[name]
		else:
			raise KeyError(name)

	def traceroute(self, sender:str, receiver:str):
		return self.dockerDaemon.containers.get(sender).exec_run("traceroute " + self.__resolve(receiver), tty=True)

	def iperf3(self, sender: str, receiver:str):
		return self.dockerDaemon.containers.get(sender).exec_run("iperf3 -c " + self.__resolve(receiver), tty=True)

	def twamp(self, sender: str, receiver:str, test_sessions:int = 2, test_sess_msgs:int = 2):
		return self.dockerDaemon.containers.get(sender).exec_run(f"/app/client -p 8000 -n {test_sessions} -m {test_sess_msgs} -s " + self.__resolve(receiver), tty=True)

	def ping(self, sender:str, receiver:str, duration:int = 5):

		out = self.dockerDaemon.containers.get(sender).exec_run(f"ping -Aqw {duration} " + self.__resolve(receiver), tty=True)
		
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
