from TestNetwork import *
a = TestNetwork()
a.connect('tcp://127.0.0.1:2375')

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

a.build(configuration)

a.ping("host1", "host2")

a.traceroute("host1", "host2")

a.iperf3("host1", "host2")

a.destroy()

