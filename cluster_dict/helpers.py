'''
Copyright 2020 John Torakis
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

def start_registry():
	from rpyc.utils.registry import UDPRegistryServer
	import threading
	regserv = UDPRegistryServer()
	reserv_thread = threading.Thread(target=regserv.start)
	reserv_thread.daemon=True
	reserv_thread.start()



def start_server(service, thread=True, host='0.0.0.0', port=18861):
	from rpyc.utils.server import ThreadedServer,ThreadPoolServer
	server = ThreadedServer(service,
			hostname=host,
			port=port,
			reuse_addr=True,
			auto_register=True,
		)
	if thread:
		import threading
		server_thread = threading.Thread(target=server.start)
		server_thread.daemon=True
		server_thread.start()
		return (host, port)
	else:
		server.start()
		return (host, port)
