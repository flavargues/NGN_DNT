'''NGN_DNT

	Wrapper around the Docker Engine to deploy containers in a star topology or fully connected. Provides a way to set up traffic control rules to add:
	- bandwidth limit,
	- delay,
	- loss,
	- dup packets,
	- corrupt packets.
	Copyright (C) 2022  flavargues @ github.com/flavargues

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License along
	with this program; if not, write to the Free Software Foundation, Inc.,
	51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
	
	Contact: @flavargues on GitHub'''
from docker import *
from docker.errors import *
from docker.types import Mount
import time, re
from progress.bar import Bar
from progress.spinner import Spinner

class DNTConfiguration():
	"""
	Example:

		>>> configuration = DNTConfiguration(
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
				thisContainer['edu.dockerTestNetwork.managed'] = "1"

				output[name] = thisContainer
			self.__labels = output
		return self.__labels
		

class DNT():
	def __init__(self):
		self.__containerList = []
		self.__networkList = []
		self.__trafficController = 0

		print('WELCOME TO 🐳 DOCKER NETWORK TESTER (DNT)     under GPL2 License             ')
		print('===========================================================================')
		print('BUILT ON 🐍 Python3 for the project of NGN class in 🏫 UniTn               ')
		print('Using :  🟢 github.com/lukaszlach/docker-tc   under MIT License             ')
		print('         🟢 github.com/emirica/twamp-protocol under GPL-2.0 License         ')
		print('         🟢 pypi.org/project/progress         under ISC License (ISCL) (ISC)')
		print('')
		print('🔑 License')
		print('NGN_DNT, Copyright © 2022 flavargues @ github.com/flavargues')
		print('NGN_DNT comes with ABSOLUTELY NO WARRANTY; for details see license file.')
		print('This is free software, and you are welcome to redistribute it')
		print('under certain conditions defined per the GPL2 License.')
		print('')
		print('         ❔ You can use DNT.help() at any moment.')
		print('')

	def license(self):
		print('🔑 License')
		print('NGN_DNT, Copyright © 2022 flavargues @ github.com/flavargues')
		print('NGN_DNT comes with ABSOLUTELY NO WARRANTY; for details see license file.')
		print('This is free software, and you are welcome to redistribute it')
		print('under certain conditions defined per the GPL2 License.')

	def help(self, helpOn:str ="all"):
		if helpOn in ['all', 'ping']:
			print('ping 	   clientHostName serverHostName durationInSec=5')
			print('	Returns a python.dict() built as such:')
			print('	* \'exit_code\'')
			print('	* \'results\'')
			print('		* \'destination\': ip of target')
			print('		* \'dataSize\': number of bytes in each packet')
			print('		* \'packetsTransmitted\'')
			print('		* \'packetsReceived\'')
			print('		* \'packetLoss\'')
			print('		* \'rtt\': Round-Trip-Time in ms')
			print('		* \'min\': minimum RTT of all packets in ms')
			print('		* \'avg\': average ''')
			print('		* \'max\': maximum ''')
			print('		* \'mdev\': Maximum Deviation ''')
			print('		* \'ipg\': InterPacket Gap ''')
			print('		* \'ewma\': Exponentially Weighted Moving Average')
			print('	* \'raw\': non parsed output of exec_run')
			print()

		'''
		traceroute clientHostName serverHostName

		iperf3     clientHostName serverHostName

		twamp      clientHostName serverHostName

		
		'''
		


	def connect(self, dockerDaemon = 'unix:///var/run/docker.sock'):
		try:
			newDaemon = DockerClient(base_url=dockerDaemon)
			if newDaemon.ping():
				print("🐳Connected to docker daemon.")
				self.dockerDaemon = newDaemon
			else:
				raise Exception("Daemon doesn't ping back.")
		except Exception:
			print(f"❌NOT connected to docker daemon at {dockerDaemon}.")
			print("You can use docker-in-docker with docker-compose up -d and enter the IP address:2376 of the container.")

	def __findInfrastructure(self):
		if len(self.dockerDaemon.containers.list(all=True)) > 0:
			for unknownContainer in self.dockerDaemon.containers.list():
				try:
					unknownContainer.reload()
					if unknownContainer.attrs['Config']["Labels"]['edu.dockerTestNetwork.managed'] == "1":
						return True
				except KeyError:
					continue
		return False

	def destroy(self):
		bar = Bar('🐳 Removing containers', max=len(self.__containerList)+3)

		for it in self.__containerList:
			try:
				it.remove(force=True)
				bar.next()
			except Exception:
				raise
		self.__containerList = []

		bar.message = '🐳 Removing Traffic Control container'
		if self.__trafficController != 0:
			self.__trafficController.remove(force=True)
		self.__trafficController = 0
		bar.next()

		bar.message = '📡 Removing network'
		self.dockerDaemon.networks.prune()
		self.__networkList = []
		bar.next()

		
		if len(self.dockerDaemon.containers.list(all=True)) > 0:
			bar.message = '⌛ Last checks'
			for unknownContainer in self.dockerDaemon.containers.list():
				try:
					unknownContainer.reload()
					if unknownContainer.attrs['Config']["Labels"]['edu.dockerTestNetwork.managed'] == "1":
						self.__containerList.append(unknownContainer)
						bar.message = '❕ Found other containers'
				except KeyError:
					continue
			
		if len(self.__containerList) > 0:
			for it in self.__containerList:
				it.remove(force=True)

		bar.message = '✔ Infrastructure destroyed.'
		bar.next()
		bar.finish()
		
	def __ensureTrafficControl(self):		
		if self.__trafficController == 0:
			
			mount1 = Mount(target="/var/run/docker.sock", source="/var/run/docker.sock")
			mount2 = Mount(target="/var/docker-tc", source="/var/docker-tc")

			mounts = list()
			mounts.append(mount1)
			mounts.append(mount2)
			
			self.__trafficController = self.dockerDaemon.containers.create("lukaszlach/docker-tc",
			name="docker-tc", cap_add=["NET_ADMIN"], network="host",
			volumes={
				'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
				'/var/docker-tc': {'bind': '/var/docker-tc', 'mode': 'rw'}
			})
			self.__trafficController.start()
			time.sleep(1)

	def build(self, networkConfig: DNTConfiguration):
		image = "flavargues/dockernetworktester"
		command="/bin/sh"
		topology = networkConfig.topology
		def __failureOnBuild(self, error:Exception, bar:Bar):
			bar.finish("❌❌❌")
			print("❌❌❌ Failure on build ! Destroying !")
			self.destroy()
			raise error

		if self.__findInfrastructure():
			print("❌ Stopped. There is still an infrastructure running. Consider running destroy().")
		else:

			bar = Bar('🐳 Starting Traffic Control', max=networkConfig.len() + 2)
			self.__ensureTrafficControl()
			bar.message = "🐳 Starting containers"
			bar.next()

			if topology == "full":
				for index, containerName in enumerate(networkConfig._params):

					try:
						myLabels = networkConfig._labels()[containerName]
						self.__networkList.append(self.dockerDaemon.networks.create("test-net"))
						newContainer = self.dockerDaemon.containers.create(image=image, command=command,
							tty=True, detach=True, cap_add=["NET_ADMIN"], name=containerName, network="test-net",
							labels=myLabels)
						self.__containerList.append(newContainer)
						newContainer.start()
					except Exception as error:
						__failureOnBuild(error, bar)
					bar.next()
			elif topology == "star":
				for index, containerName in enumerate(networkConfig._params):
					try:
						if index == 0:
							for j in range(1, networkConfig.len()):
								self.__networkList.append(self.dockerDaemon.networks.create(f"b0-{j}"))

							newContainer = self.dockerDaemon.containers.create(image=image, command=command,
								tty=True, detach=True, cap_add=["NET_ADMIN"], name=containerName,
								labels=networkConfig._labels()[containerName])
							self.__containerList.append(newContainer)

							for it in self.__networkList:
								it.connect(networkConfig.names()[0])
							
						else:
							newContainer = self.dockerDaemon.containers.create(image=image, command=command,
								tty=True, detach=True, cap_add=["NET_ADMIN"], name=containerName,
								labels=networkConfig._labels()[containerName], network=f"b0-{index}")
							self.__containerList.append(newContainer)
						newContainer.start()
					except Exception as error:
						__failureOnBuild(error, bar)
					bar.next()
				
				gateways = dict()
				center = self.__containerList[0]
				center.reload()
				for network in self.__networkList:
					network.reload()
					gateways[network.name] = center.attrs['NetworkSettings']['Networks'][network.name]['IPAddress']
				
				output = list()
				for edge in self.__containerList[1:]:
					edge.reload()
					myNetwork = list(edge.attrs['NetworkSettings']['Networks'])[0]
					myGateway = gateways[myNetwork]
					command = f"ip route add default via {myGateway}"
					output.append( edge.exec_run("ip route del default", tty=True) )
					time.sleep(0.5)
					output.append( edge.exec_run(f"ip route add default via {myGateway}", tty=True) )
				
			
			bar.message = "✔ Infrastructure built."
			self.__IPTable = {}
			for it in self.__containerList:
				it.reload()
				itOneNetwork = list(it.attrs['NetworkSettings']['Networks'].keys())[0]
				itIP = it.attrs['NetworkSettings']['Networks'][itOneNetwork]["IPAddress"]
				self.__IPTable[ str(it.name) ] = ( str(itIP) )
			bar.next()
			bar.finish()
		
	def __resolve(self, name: str):
		if name in self.__IPTable:
			return self.__IPTable[name]
		else:
			raise KeyError(name)

	def ping(self, sender:str, receiver:str, duration:int = 5):
		print('⌛ Running PING')
		answer = self.dockerDaemon.containers.get(sender).exec_run(f"ping -Aqw {duration} " + self.__resolve(receiver), tty=True)
		output = str(answer.output)
		try:
			resultsDict = dict([
				('destination', re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output).group(0)),
				('dataSize', re.search('\((\d{1,})\) bytes', output).groups()[0]),

				('packetsTransmitted', re.search('(\d{1,}) packets tra', output).groups()[0]),
				('packetsReceived', re.search('(\d{1,}) re', output).groups()[0]),
				('packetLoss', re.search('(\S+)%', output).group()[0]),

				('rtt', re.search('time (\d{1,})ms', output).groups()[0]),
				('min', re.search('mdev = (\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})', output).groups()[0]),
				('avg', re.search('mdev = (\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})', output).groups()[1]),
				('max', re.search('mdev = (\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})', output).groups()[2]),
				('mdev',re.search('mdev = (\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})\/(\d{1,}\.\d{1,})', output).groups()[3]),

				('ipg', re.search('ewma (\d{1,}\.\d{1,})', output).groups()[0]),
				('ewma', re.search('ewma \d{1,}\.\d{1,}\/(\d{1,}\.\d{1,})', output).groups()[0])
			])

			feedback = dict([  ('exit_code', answer.exit_code), ('results', resultsDict), ('raw', answer.output)  ])
			
			return feedback
		except Exception as err:
			print('❕ Parsing failed. Returning raw data.')
			return answer, err

	def traceroute(self, sender:str, receiver:str):
		print('⌛ Running traceroute')
		answer = self.dockerDaemon.containers.get(sender).exec_run("traceroute " + self.__resolve(receiver), tty=True)
		
		output = str(answer.output)
		try:
			routes = output.split('\\r\\n')
			routes.pop()
			routes.pop(0)

			hops = list()
			for trace in routes:
				try:
					hop1 = re.findall('(\d+\.\d+|\*) ms', trace)[0]
				except:
					hop1 = ''
				try:
					hop2 = re.findall('(\d+\.\d+|\*) ms', trace)[1]
				except:
					hop2 = ''
				try:
					hop3 = re.findall('(\d+\.\d+|\*) ms', trace)[2]
				except:
					hop3 = ''
				hops.append(dict([
					('hopNumber', re.search('^ (\d+)', trace).groups()[0]),
					('host.Interface', re.search('(\w\S+|\*)', trace).groups()),
					('targetIP', re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', trace).group()),
					('hop1', hop1),
					('hop2', hop2),
					('hop3', hop3)
				]))

			resultsDict = dict([
				('destination', re.search('(\d{1,}\.\d{1,}\.\d{1,}\.\d{1,})', output).groups()[0]),
				('dataSize', re.search('(\d{1,}) byte', output).groups()[0]),
				('hops', hops)
			])
			feedback = dict([  ('exit_code', answer.exit_code), ('results', resultsDict), ('raw', answer.output)  ])
			
			return feedback
		except Exception as err:
			print('❕ Parsing failed. Returning raw data.')
			return answer, err

	def iperf3(self, sender: str, receiver:str):
		print('⌛ Running iperf3')
		answer = self.dockerDaemon.containers.get(sender).exec_run("iperf3 -c " + self.__resolve(receiver), tty=True)
		try:
			output = str(answer.output)
			lines = output.split('\\r\\n')

			while "- - - " not in lines[0]:
				lines.pop(0)
			lines.pop(0)
			lines.pop(0)
			lines.remove('iperf Done.')
			lines.remove('')
			lines.remove('\'')
			

			steps = list()
			for line in lines:
				role = re.findall('(sender|receiver)', line)[0]
				interval = re.findall('\]\s+(.+  sec)', line)[0]
				transfer = re.findall('(\d+)\s+\wBytes', line)[0]
				bitrate = re.findall('(\d+)\s+\w+bits', line)[0]
				try:
					retr = re.findall('\/sec\s+(\d+)', line)[0]
				except IndexError:
					retr = ''

				steps.append([
					('role', role),
					('interval', interval),
					('transfer', transfer),
					('bitrate', bitrate),
					('retries', retr)
				])

			feedback = dict([  ('exit_code', answer.exit_code), ('results', steps), ('raw', answer.output)  ])
			return feedback
		except Exception as err:
			return answer, err

	def twamp(self, sender: str, receiver:str, test_sessions:int = 2, test_sess_msgs:int = 2):
		print('⌛ Running TWAMP')
		out = self.dockerDaemon.containers.get(sender).exec_run(f"/app/client -p 8000 -n {test_sessions} -m {test_sess_msgs} -s " + self.__resolve(receiver), tty=True)
		return out
