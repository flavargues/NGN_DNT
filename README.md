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

## Quick Install

```bash
git clone https://github.com/flavargues/NGN_DNT.git
cd NGN_DNT
docker build -t flavargues/dockernetworktester ./dockerNetworkTester/
pip install -r requirements.txt
```

Use the example file or:
In a python3 interactive shell or in .py file:
```python
from TestNetwork import *
dockerTestNetwork = DNT()
dockerTestNetwork.connect()
#Or give the socket to your docker daemon (see https://docs.docker.com/engine/reference/commandline/dockerd/)

#Your configuration here
#Your tests here

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
NGN_DNT recognizes the following labels:
> excerpt from lukaszlach/docker-tc at https://github.com/lukaszlach/docker-tc
* `com.docker-tc.enabled` - when set to `True` the container network rules will be set automatically, any other value or if the label is not specified - the container will be ignored
*  `com.docker-tc.limit` - bandwidth or rate limit for the container, accepts a floating point number, followed by a unit, or a percentage value of the device's speed (e.g. 70.5%). Following units are recognized:
    * `bit`, `kbit`, `mbit`, `gbit`, `tbit`
    * `bps`, `kbps`, `mbps`, `gbps`, `tbps`
    * to specify in IEC units, replace the SI prefix (k-, m-, g-, t-) with IEC prefix (ki-, mi-, gi- and ti-) respectively
* `com.docker-tc.delay` - length of time packets will be delayed, accepts a floating point number followed by an optional unit:
    * `s`, `sec`, `secs`
    * `ms`, `msec`, `msecs`
    * `us`, `usec`, `usecs` or a bare number
* `com.docker-tc.loss` - percentage loss probability to the packets outgoing from the chosen network interface
* `com.docker-tc.duplicate` - percentage value of network packets to be duplicated before queueing
* `com.docker-tc.corrupt` - emulation of random noise introducing an error in a random position for a chosen percent of packets

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
> returns a python.dict() built as such:
> 'destination': ip of target
> 'dataSize': number of bytes in each packet
> 'packetsTransmitted'
> 'packetsReceived'
> 'packetLoss'
> 'rtt': Round-Trip-Time in ms
> 'min': minimum RTT of all packets in ms
> 'avg': average ''
> 'max': maximum ''
> 'mdev': Maximum Deviation ''
> 'ipg': InterPacket Gap ''
> 'ewma': Exponentially Weighted Moving Average ''

````python
dockerTestNetwork.traceroute("host1", "host2")
````
> WIP

````python
dockerTestNetwork.iperf3("host1", "host2")
````
> WIP

````python
dockerTestNetwork.twamp("host1", "host2")
````
> WIP

## License

Licensed under the GPL2 License. Refer to the License file.