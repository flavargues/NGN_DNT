# NGN_project

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

- [Python >= 3](http://docs.python-guide.org/en/latest/starting/installation/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [Docker](https://www.docker.com/products/docker) (Recommended)

## Quick Install

```bash
cd NGN_project
docker build -t flavargues/testerimage ./testerImage/
pip install -r requirements.txt
```

In a python3 interactive shell:
```python
from TestNetwork import *
TestNet = TestNetwork()
TestNet.connect('tcp://127.0.0.1:2375')

#your code here

a.destroy()
```

### Writing and Building your configuration

Not written
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

TestNet.build(configuration)
```

Not written
## Run your tests

````python
a.ping("host1", "host2")
a.traceroute("host1", "host2")
a.iperf3("host1", "host2")
a.twamp("host1", "host2")
```


## Authors

Me, myself and I
Not written

## License
To be defined
Not written

