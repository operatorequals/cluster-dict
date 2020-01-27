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

import argparse
import json
from pprint import pprint, pformat
import rpyc
import random
from time import sleep

from rpyc.utils.factory import discover

from cluster_dict.service import ClusterDictService
from cluster_dict import ClusterDict # ; cd = ClusterDict()
from cluster_dict.logger import logger

parser = argparse.ArgumentParser()
parser.add_argument("--name", '-n', help="ClusterDict name",default='ClusterDict')

subparsers = parser.add_subparsers(dest='mode')
subparsers.required = True

disc_ = subparsers.add_parser("discover")

set_ = subparsers.add_parser("set")
set_.add_argument("key")
set_.add_argument("value")

get_ = subparsers.add_parser("get")
get_.add_argument("key")

update_ = subparsers.add_parser("update")
update_.add_argument("JSON", type=argparse.FileType('r'))

serve_ = subparsers.add_parser("serve")
serve_.add_argument("--JSON", type=argparse.FileType('r'))

args = parser.parse_args()

# print(args)
if args.mode == 'discover':
	try:
		conn_tuples = discover(args.name)
		for conn_tuple in conn_tuples:
			print("Connecting to {}".format(conn_tuple))
			conn = rpyc.connect(*conn_tuple)
			serv = conn.root
			print("~ Dumping:")
			pprint(serv.sync())
			conn.close()

	except rpyc.utils.factory.DiscoveryError as de:
		print(de)

if args.mode == 'set':
	try:
		conn_tuples = discover(args.name)
		for conn_tuple in conn_tuples:
			print("Connecting to {}".format(conn_tuple))
			conn = rpyc.connect(*conn_tuple)
			serv = conn.root
			# Keep the types of the key and value from CLI
			key = eval(args.key)
			value = eval(args.value)
			print("~ '{}[{}] = {}'".format(
				args.name, key, value
				)
			)
			serv.set(key, value)
			conn.close()
	except rpyc.utils.factory.DiscoveryError as de:
		print(de)

if args.mode == 'get':
	try:
		conn_tuples = discover(args.name)
		for conn_tuple in conn_tuples:
			print("Connecting to {}".format(conn_tuple))
			conn = rpyc.connect(*conn_tuple)
			serv = conn.root
			# Keep the type of the key from CLI
			key = eval(args.key)
			print("~ '{}[{}]'".format(
				args.name, key
				)
			)
			print(serv.get(key))
			conn.close()
	except rpyc.utils.factory.DiscoveryError as de:
		print(de)

if args.mode == 'update':
	data = json.load(args.JSON)
	print ('{}.update("{}")'.format(args.name, pformat(data)))
	try:
		cd = ClusterDict(store=data, name=args.name)
		# cd.sync()
	except rpyc.utils.factory.DiscoveryError as de:
		print(de)

if args.mode == 'serve':
	if args.JSON:
		data = json.load(args.JSON)	
	else:
		data = None
	print ('{}("{}")'.format(args.name, pformat(data)))
	try:
		cd = ClusterDict(store=data, name=args.name)
		import code
		code.interact(local=locals())

	except rpyc.utils.factory.DiscoveryError as de:
		print(de)
	except KeyboardInterrupt as ki:
		cd.service.close_down()
		print("Aborted by the user")
