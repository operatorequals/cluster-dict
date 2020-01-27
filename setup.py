from setuptools import setup


import cluster_dict

try :
	long_description_str = open('README.md').read()
except IOError as e:
	long_description_str = 'https://github.com/operatorequals/cluster_dict/blob/master/README.md'



setup(name='cluster_dict',
	  version=cluster_dict.__version__,
	  description='Distributed Python dict',
	  long_description=long_description_str,
	  author=cluster_dict.__author__,
	  author_email='john.torakis@gmail.com',
	  license='Apache2',
	  url=cluster_dict.__github__,
	  py_modules=['cluster_dict'],
	  classifiers=[
		# 'Development Status :: 6 - Mature',

		'License :: OSI Approved :: Apache Software License',

		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.7',

		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy',

 		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',

		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Software Development :: Build Tools',
		'Topic :: Software Development :: Testing',

		

	],
	keywords = ['dict',
		'distributes',
		'key-value',
		],

	# entry_points = {
	# 	'console_scripts' : [
	# 			"cluster_dict="
	# 		]
	# 	}
	)
