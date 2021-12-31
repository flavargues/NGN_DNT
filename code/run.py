from TestNetwork import *
a = TestNetwork()
a.connect('tcp://127.0.0.1:2375')

configuration = TestNetworkConfiguration(
	topology="full",
	names=    ["host0", "host1", "host2", "host3"],
	throttled=["True" ,"True"  ,"True"  ,"True"  ],
	bandwidth=["1mbps","1mbps" ,"1mbps" ,"1mbps" ],
	delay=    ["100ms","100ms" ,"100ms" ,"100ms" ],
	loss=     ["50%"  ,"50%"   ,"50%"   ,"50%"   ],
	duplicate=["0%"   ,"0%"    ,"0%"    ,"0%"    ],
	corrupt=  ["0%"   ,"0%"    ,"0%"    ,"0%"    ]
)

#print(configuration._labels())

a.build(configuration)
a.destroy()

