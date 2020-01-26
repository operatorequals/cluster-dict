import rpyc
from rpyc.utils.factory import discover


# __all__=['get', 'set', 'del']


import threading
from random import choice, randint
import collections
import time

from cluster_dict.helpers import start_registry, start_server
from cluster_dict.service import ClusterDictService

try:
	start_registry()
except OSError:
	print("Unable to start Registry, continuing...")



# Started from:
#	https://stackoverflow.com/questions/3387691/how-to-perfectly-override-a-dict
class ClusterDict(collections.MutableMapping):
	"""A dictionary that applies an arbitrary key-altering
	   function before accessing the keys"""

	# def __init__(self, *args, **kwargs):
	def __init__(self, *args, name="DefaultClusterDict",
								store={},
								sync_interval = 10,
								# sync_percentage = 100,
								authenticator = None,	# Can be any of 'rpyc.utils.authenticators'
								**kwargs):
		self.name = name
		self.SERVER = False

		class PrivateClusterDictService(ClusterDictService):
			ALIASES=[name, *ClusterDictService.ALIASES]
			def __init__(self,*args,**kwargs): super().__init__()
		self.service = PrivateClusterDictService(
				dict=store,
				sync_interval=sync_interval
			)
		self.store = self.service

		self.survive_thread = threading.Thread(target=self.survive_thread_func)
		self.survive_thread.daemon = True
		self.survive_thread.start()

		self.cluster_connect()
		# self.start_server()

	# ========================================================
	def __getitem__(self, key):
		return self.store.get(self.__keytransform__(key))

	def __setitem__(self, key, value):
		self.store.set(self.__keytransform__(key), value)

	def __delitem__(self, key):
		del self.store[self.__keytransform__(key)]

	def __iter__(self):
		return iter(self.store)

	def __len__(self):
		return len(self.store)

	def __keytransform__(self, key):
		return key

	def __repr__(self):
		return self.store._data.__repr__()
	# ========================================================

	def cluster_connect(self, max_connections=1):
		try:
			con_tuples = discover(self.name)
			print("[!] Discovered", con_tuples)
			# con_tuple = choice(con_tuples)
			for i in range(max_connections):
				con_tuple = con_tuples[i]
				self.conn = rpyc.connect(*con_tuple, service=self.service)
			return True
		except rpyc.utils.factory.DiscoveryError as de:
			print (de)
			return False

	def survive_thread_func(self, interval=3):
		while True:
			# If the server is on - do nothing
			if self.SERVER: continue
			for conn in self.service.connections:
				try: conn.ping()
				except EOFError: pass
			if not self.service.connections:
				if not self.cluster_connect():
					time.sleep(randint(0,8))
				if not self.cluster_connect():
					print("Starting server!")
					self.start_server()
					self.SERVER = True
			time.sleep(interval)

	def sync(self):
		self.service.sync()

	def start_server(self):
		try:
			start_registry()
		except OSError:
			print("Unable to start Registry, continuing...")
		try:
			start_server(self.service, thread=False)
			self.SERVER=True
		except OSError:
			self.SERVER=False
