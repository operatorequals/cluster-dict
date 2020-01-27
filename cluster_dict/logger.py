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

# Taken from:
#	https://github.com/satori-ng/satori-core/blob/develop/satoricore/logger.py
import logging

try:
	from termcolor import colored
except ImportError:
	def colored(*args, **kwargs):
		return args[0]

LOG_LEVEL = logging.INFO

# Found in:
# 'https://stackoverflow.com/questions/14844970/modifying-logging-message-format-based-on-message-logging-level-in-python3'

class SymbolLogFormatter(logging.Formatter):

	def __init__(self, fmt="%(levelno)s: %(msg)s", uuid=None, name=None):
		super().__init__(fmt=fmt, datefmt=None, style='%')
		if uuid and name:

			mod_tag = "<{name}:{uuid}>".format(name=name, uuid=uuid)
		else:
			mod_tag = ""

		self.dbg_fmt  = colored(
			"[@]{} %(module)s: %(lineno)d: %(msg)s"
			.format(mod_tag),
			"grey", "on_green"
			)
		self.crit_fmt = colored("[X]{} %(msg)s".format(mod_tag), "red", attrs=["bold"])
		self.err_fmt  = colored("[-]{} %(msg)s".format(mod_tag), "red")
		self.warn_fmt = colored("[!]{} %(msg)s".format(mod_tag), "green")
		self.info_fmt = colored("[+]{} %(msg)s".format(mod_tag), "cyan")

	def format(self, record):

		# Save the original format configured by the user
		# when the logger formatter was instantiated
		format_orig = self._style._fmt

		# Replace the original format with one customized by logging level
		if record.levelno == logging.DEBUG:
			self._style._fmt = self.dbg_fmt

		elif record.levelno == logging.INFO:
			self._style._fmt = self.info_fmt

		elif record.levelno == logging.ERROR:
			self._style._fmt = self.err_fmt

		elif record.levelno == logging.WARN:
			self._style._fmt = self.warn_fmt

		elif record.levelno == logging.CRITICAL:
			self._style._fmt = self.crit_fmt

		# Call the original formatter class to do the grunt work
		result = logging.Formatter.format(self, record)

		# Restore the original format configured by the user
		self._style._fmt = format_orig

		return result


handler = logging.StreamHandler()
fmt = SymbolLogFormatter()
handler.setFormatter(fmt)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)


def set_quiet_logger():
	global logger
	logger.setLevel(logging.WARN)


def set_debug_logger():
	global logger
	logger.setLevel(logging.DEBUG)

