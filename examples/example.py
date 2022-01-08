## Licensed under the GPL2 License. Refer to the License file.
from DNT import *
myInstance = DNT()
myInstance.connect()

configuration = DNTConfiguration(
	topology="star",
	names=    ["host0", "host1", "host2", "host3"    ],
	throttled=["True" ,"True"  ,"True"  ,"True"      ],
	bandwidth=["20mbps","20mbps" ,"20mbps" ,"20mbps" ],
	delay=    ["100ms","100ms" ,"100ms" ,"100ms"     ],
	loss=     ["10%"  ,"10%"   ,"10%"   ,"10%"       ],
	duplicate=["0%"   ,"0%"    ,"0%"    ,"0%"        ],
	corrupt=  ["0%"   ,"0%"    ,"0%"    ,"0%"        ]
)

myInstance.build(configuration)

ping = myInstance.ping("host1", "host2")
traceroute = myInstance.traceroute("host1", "host2")
iperf3 = myInstance.iperf3("host1", "host2")
twamp = myInstance.twamp("host1", "host2")

myInstance.destroy()
