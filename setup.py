from setuptools import setup

from cluster_dict import __meta__ as cluster_dict

try :
	long_description_str = open('README.md').read()
except IOError as e:
	long_description_str = 'https://github.com/operatorequals/cluster_dict/blob/master/README.md'

def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]

setup(
	name=cluster_dict.__name__,
	version=cluster_dict.__version__,
	description='Distributed Python dict',
	long_description=long_description_str,
	author=cluster_dict.__author__,
	author_email=cluster_dict.__email__,
	license='Apache2',
	url=cluster_dict.__github__,
	py_modules=['cluster_dict'],

	install_requires=load_requirements("requirements.txt"),

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
	keywords = [
		'dict',
		'distributes',
		'key-value',
	],

	entry_points = {
		'console_scripts' : [
				"cluster_dict=cluster_dict.__main__:main"
		]
	}
)
