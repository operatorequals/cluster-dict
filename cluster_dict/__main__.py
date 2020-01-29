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
import sys
from time import sleep

from rpyc.utils.factory import discover

from cluster_dict.service import ClusterDictService
from cluster_dict import ClusterDict
from cluster_dict.logger import logger

def _prepare_arguments():
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

	serve_ = subparsers.add_parser("serve")
	serve_.add_argument("--json-file", '-f', type=argparse.FileType('r'))
	serve_.add_argument("--host", default='0.0.0.0')
	serve_.add_argument("--port", '-p', default=18861)
	serve_.add_argument("--exit", default=False, action='store_true')

	return parser.parse_args()

def main_exec(args):
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
		except AttributeError:
			conn.close()

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

	if args.mode == 'serve':
		if args.json_file:
			data = json.load(args.json_file)	
		else:
			data = {}
		print ('{}({})'.format(args.name, pformat(data)))
		try:
			cd = ClusterDict(store=data, name=args.name)
			if args.exit:
				cd.sync()
				cd.disconnect()
				sys.exit(0)

			import code
			code.interact(local=locals(),
				banner="""
================================================
Variable 'cd' contains ClusterDict "{name}"
================================================
	""".format(name=args.name)
				)
			# Reached here after killing Interactive console
			cd.service.close_down()
		except rpyc.utils.factory.DiscoveryError as de:
			print(de)
		except KeyboardInterrupt as ki:
			cd.service.close_down()
			print("Aborted by the user")


def main():
	args = _prepare_arguments()
	main_exec(args)

if __name__ == '__main__':

	main()
