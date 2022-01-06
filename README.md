# NGN_DNT

Wrapper around the Docker Engine to deploy containers in a star topology or fully connected. Provides a way to set up traffic control rules to add:
- bandwidth limit,
- delay,
- loss,
- dup packets,
- corrupt packets.

Provides the following test tools:
- ping
- traceroute
- iperf3
- TWAMP (Two-Way Active Measurement Protocol)

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
dockerTestNetwork.connect()#Or give the socket to your docker daemon (see https://docs.docker.com/engine/reference/commandline/dockerd/)

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
For further details, refer to the documentation of lukaszlach/docker-tc at https://github.com/lukaszlach/docker-tc#:~:text=Docker%20Traffic%20Control%20recognizes,chosen%20percent%20of%20packets

This command will build the configuration you have defined. If containers created by another instance are still running, it will refuse to build.
```python
dockerTestNetwork.build(configuration)
```

## Writing and Building tests

````python
dockerTestNetwork.ping("host1", "host2")
dockerTestNetwork.traceroute("host1", "host2")
dockerTestNetwork.iperf3("host1", "host2")
dockerTestNetwork.twamp("host1", "host2")
```

## License

Licensed under the GPL2 License. Refer to the License file.