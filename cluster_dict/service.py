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

import logging
from os import linesep
import rpyc
import threading
import time

from uuid import uuid4

NULL_META_VALUE = {'value':None, 'ts':-1, 'lu':-1}

class ClusterDictService (rpyc.core.service.ClassicService):
	ALIASES = ["ClusterDict", "CLUSTER-DICT"]

	def __init__(self, **kwargs):
		rpyc.core.service.ClassicService.__init__(self)

		self.uuid = kwargs.get('uuid', str(uuid4()))
		self.logger = kwargs.get('logger', logging.getLogger(
				"ClusterDictService:({})".format(self.uuid)
				)
			)
		self.cluster_dict_name = kwargs.get('name', 'N/A')
		self._data = {}
		store = kwargs.get('store', dict())
		print(store)
		for k,v in store.items():
			self.set(k, v)
		self.sync_interval = kwargs.get('sync_interval', 2)
		self.propagation_grade = kwargs.get('propagation_grade', 3)

		self.logger.info("Service with UUID '{}' created!".format(self.uuid))

		self.connections = []
		self.connection_uuids = []
		sync_thread = threading.Thread(target=self.sync_thread)
		sync_thread.daemon = True
		sync_thread.start()

	def exposed_uuid(self):
		return self.uuid

	def on_connected(self, conn):
		self.on_connect(conn)

	def on_connect(self, conn):
		try:
			ruuid = conn.root.uuid()
			self.logger.debug("Connecting with [{}]!".format(ruuid))
			if ruuid == self.uuid:
				self.logger.info("Connected to self. Disconnecting...")
				conn.close()
				return
			if ruuid in self.connection_uuids:
				self.logger.info(
						"Already Connected to remote ClusterDict [{}]. Disconnecting...".format(ruuid)
					)
				conn.close()
				return
		except AttributeError as ae:
			print(ae)
			self.logger.debug("The client is not a ClusterDictService")
			return

		self.logger.info("Connected with [{}]!".format(ruuid))
		serv = conn.root
		self.connections.append(conn)
		self.connection_uuids.append(ruuid)

		self.logger.debug("Attempting sync with [{}]!".format(ruuid))
		self.sync()	# Force remote service to sync

	def on_disconnect(self, conn):
		try:
			self.connections.remove(conn)
			ruuid = conn.root.uuid()
			self.logger.info("Disconnected from [{}]!".format(ruuid))
			self.connection_uuids.remove(ruuid)
		except AttributeError as ae:
			self.logger.debug("Disconnected from unknown service!")
		except ValueError as ve:
			# print("Connection has been aborted")
			pass

	def set_meta(self, key, value):
		self._data[key] = value

	def set(self, key, value):
		ts = int(time.time())
		lu = ts
		self.logger.debug(linesep + 
			"{cd_name}[{key}] = {value} # (@ {ts})".format(
				cd_name=self.cluster_dict_name,
				key=key, value=value, ts=ts
				)
			)
		self._data[key] = {
				'value':value,
				'ts':ts, 'lu':lu
			}

	def exposed_set(self, key, value):
		self.set(key, value)

	def get(self, key, cache=True):
		if key not in self._data:
			v = self.ask_for(key)
			if v is NULL_META_VALUE: raise KeyError(key)
			if cache : self.set_meta(key, v)
			return v['value']
		else:
			return self._data[key]['value']

	def ask_for(self, key, propagation=None):
		if propagation is None:
			propagation = self.propagation_grade
		self.logger.info(
			"Asking cluster for '{cd_name}[{key}]' (propagation={p})".format(
				cd_name=self.cluster_dict_name, key=key, p=propagation
				)
			)
		final = NULL_META_VALUE
		for conn in self.connections:
			serv = conn.root
			# print("asking ", conn)
			# Iterate through everyone and ask for the key
			v=serv.get_meta(key, propagation=propagation)
			if v != NULL_META_VALUE:
				if v['ts'] > final['ts']:
					final = v
					v['lu'] = int(time.time())
		return final

	def exposed_get(self, key):
		return self.get(key)

	def exposed_get_meta(self, key, propagation):
		if propagation <= 0 : return NULL_META_VALUE
		self.logger.debug(
			"Asked cluster for '{cd_name}[{key}]' (propagation={p})".format(
				cd_name=self.cluster_dict_name, key=key, p=propagation
				)
			)
		try:
			return self._data[key]
		except KeyError:
			# print("Propagating for '{}'".format(key))
			v = self.ask_for(key, propagation=(propagation-1))
			return NULL_META_VALUE

	def exposed_sync(self):
		return self._data

	def sync_thread(self):
		while True:
			time.sleep(self.sync_interval)
			self.sync()

	def sync(self):
		for conn in self.connections:
			# print("Syncing with connection: ", conn)
			serv = conn.root
			try:
				netref_sync_dict = serv.sync()
				# sync_dict = netref_sync_dict.value
				# netref_sync_dict.wait()
				# Use a callback to sync properly
				sync_dict = netref_sync_dict
			except Exception as ae:
				# The client is not a ClusterDictService
				continue
			try:
				self.__update_dict(sync_dict)
			except RuntimeError as re:
				print(re)

	def __update_dict(self, sync_dict):
		# Iterate over foreign data
		for k in sync_dict:
			# If key exists in both dicts
			# print("Syncing k '{}'".format(k))
			if k in self._data:
				lts = self._data[k]['ts']
				rts = sync_dict[k]['ts']
				# Compare TimeStamps
				if rts > lts:
					print("Changing '{}' to {}".format(k, sync_dict[k]))
					self._data[k] = sync_dict[k]
					self.logger.debug("Altering:"+ linesep + 
						"{cd_name}[{key}] = {value} # (@ {ts})".format(
							cd_name=self.cluster_dict_name,
							key=k, value=sync_dict[k]['value'], ts=sync_dict[k]['ts']
							)
						)
			else:
				self._data[k] = sync_dict[k]
				self.logger.debug("Adding:"+ linesep + 
					"{cd_name}[{key}] = {value} # (@ {ts})".format(
						cd_name=self.cluster_dict_name,
						key=k, value=sync_dict[k]['value'], ts=sync_dict[k]['ts']
						)
					)

	def close_down(self):
		self.logger.warning("Tearing down connections!")
		for conn in self.connections:
			conn.close()
			self.connections = []
			self.connection_uuids = []