
def start_registry():
	from rpyc.utils.registry import UDPRegistryServer
	import threading
	regserv = UDPRegistryServer()
	reserv_thread = threading.Thread(target=regserv.start)
	reserv_thread.daemon=True
	reserv_thread.start()



def start_server(service, port=18861, thread=True):
	from rpyc.utils.server import ThreadedServer
	server = ThreadedServer(service,
			port=port,
			reuse_addr=True,
			auto_register=True,
		)
	if thread:
		import threading
		server_thread = threading.Thread(target=server.start)
		server_thread.daemon=True
		server_thread.start()
	else:
		server.start()