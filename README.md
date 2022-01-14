# NGN_DNT

Wrapper around the Docker Engine to deploy containers in a star topology or fully connected. Provides a way to set up traffic control rules to add:
- bandwidth limit,
- delay,
- loss,
- dup packets,
- corrupt packets.

Provides the following test tools:
- ping,
- traceroute,
- iperf3,
- TWAMP (Two-Way Active Measurement Protocol).

## Software requirements
Works with traffic control only on Unix systems. Tested successfully on Ubuntu Server 20.04 LTS.

- [Python >= 3](http://docs.python-guide.org/en/latest/starting/installation/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [Docker](https://www.docker.com/products/docker)

## DISCLAIMER
WE DO NOT GUARANTEE THAT THIS PROGRAM WILL NOT MESS UP YOUR CONTAINERS ON YOUR SYSTEM. PLEASE SAVE ALL YOUR CONTAINERS BEFORE USING THIS SOFTWARE. You can also use Docker-in-Docker with the docker-compose file in /util, with no more guarantee than stated previously.

## Quick Install
```bash
git clone https://github.com/flavargues/NGN_DNT.git
cd NGN_DNT
docker build -t flavargues/dockernetworktester ./dockerImage/
pip install -r requirements.txt
```

### Usage
You may run the project in a .py file with all the tests written  or in a jupyter notebook (see /example files).
You can also run it in a python interactive shell.

Import the DNT class and instiantiate one.
```python
from TestNetwork import *
dockerTestNetwork = DNT()
```

Connect to instance to the docker daemon. By default, it connects to the unix socket at unix:///var/run/docker.sock.
```python
dockerTestNetwork.connect()
```
You can also give the connect() function the socket of the docker daemon as a string. 

➡**Your configuration here (see below)**  
➡**Your tests here (see below)**  

Don't forget to destroy your infrastructure by running this function ! It will remove the containers and networks created by the program.
```python
dockerTestNetwork.destroy()
```

### Writing and Building your configuration

```python
configuration = TestNetworkConfiguration(
    topology="star",
    names=    ["host0", "host1", "host2", "host3"    ],
    throttled=["True" ,"True"  ,"True"  ,"True"      ],
    bandwidth=["20mbps","20mbps" ,"20mbps" ,"20mbps" ],
    delay=    ["100ms","100ms" ,"100ms" ,"100ms"     ],
    loss=     ["10%"  ,"10%"   ,"10%"   ,"10%"       ],
    duplicate=["0%"   ,"0%"    ,"0%"    ,"0%"        ],
    corrupt=  ["0%"   ,"0%"    ,"0%"    ,"0%"        ]
)
```
❌❌❌ The more traffic control you set, the more chance there is that tests will straight out fail ! It is recommended to set reasonable values. The parsing of results might fail as well.  
NGN_DNT recognizes the following labels:
* `topology` - the topology to be created:
    * `star`: first host defined will be in the center, the others will be connected only to the center.
    * `full`: all nodes are connected to the same network.
* `names`: any valid str()
> EDITED excerpt from lukaszlach/docker-tc at https://github.com/lukaszlach/docker-tc
* `throttled` - when set to `True` the container network rules will be set automatically, any other value or if the label is not specified - the container will be ignored
*  `bandwidth` - bandwidth or rate limit for the container, accepts a floating point number, followed by a unit, or a percentage value of the device's speed (e.g. 70.5%). Following units are recognized:
    * `bit`, `kbit`, `mbit`, `gbit`, `tbit`
    * `bps`, `kbps`, `mbps`, `gbps`, `tbps`
    * to specify in IEC units, replace the SI prefix (k-, m-, g-, t-) with IEC prefix (ki-, mi-, gi- and ti-) respectively
* `delay` - length of time packets will be delayed, accepts a floating point number followed by an optional unit:
    * `s`, `sec`, `secs`
    * `ms`, `msec`, `msecs`
    * `us`, `usec`, `usecs` or a bare number
* `loss` - percentage loss probability to the packets outgoing from the chosen network interface
* `duplicate` - percentage value of network packets to be duplicated before queueing
* `corrupt` - emulation of random noise introducing an error in a random position for a chosen percent of packets

> Read the [tc command manual](http://man7.org/linux/man-pages/man8/tc.8.html) to get detailed information about parameter types and possible values.


```python
dockerTestNetwork.build(configuration)
```
This command will build the configuration you have defined. If containers created by another instance are still running, it will refuse to build.

## Writing and Building tests

You have access to functions that run tests for:
- ping,
- traceroute,
- iperf3,
- TWAMP (Two-Way Active Measurement Protocol).
All functions take 2 string arguments that are the client and server hosts.

````python
dockerTestNetwork.ping("host1", "host2")
````
Returns a python.dict() built as such:
* exit_code
* results
  * destination: ip of target
  * dataSize: number of bytes in each packet
  * packetsTransmitted
  * packetsReceived
  * packetLoss
  * rtt: Round-Trip-Time in ms
  * min: minimum RTT of all packets in ms
  * avg: average ''
  * max: maximum ''
  * mdev: Maximum Deviation ''
  * ipg: InterPacket Gap ''
  * ewma: Exponentially Weighted Moving Average ''
* raw: non parsed output of exec_run

````python
dockerTestNetwork.traceroute("host1", "host2")
````
Returns a python.dict() built as such:
* exit_code
* results
  * destination
  * dataSize
  * hops : list()
    * hopNumber
    * host.Interface
    * targetIP
    * hop1
    * hop2
    * hop3
* raw: non parsed output of exec_run

````python
dockerTestNetwork.iperf3("host1", "host2")
````
Returns a python.dict() built as such:
* exit_code
* steps : list()
  * role
  * intervak
  * trasnfer
  * bitrate
  * retries
* raw: non parsed output of exec_run

````python
dockerTestNetwork.twamp("host1", "host2")
````
The output of TWAMP is too unpredictable, parsing is too difficult and will not bring value. It will not be implemented.  
All parsings are dependent on a predictable output of the tests. If tests fail or return a non predictable output, except the parsing to not be done and receive the raw output.  

## License

Licensed under the GPL2 License. Refer to the License file.
