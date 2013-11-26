#   yadtreceiver
#   Copyright (C) 2012 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
    Use the function Configuration.load to read a Configuration from a file.

    example configuration file receiver.cfg:

        [receiver]
        log_filename = /var/log/yadtreceiver.log
        targets = devyadt, proyadt
        targets_directory = /etc/yadtshell/targets
        script_to_execute = /usr/bin/yadtshell

        [broadcaster]
        host = broadcaster.domain.tld
        port = 8081

"""

__author__ = 'Michael Gruber'

from glob import glob
import os
import socket
from yadtcommons.configuration import YadtConfigParser


DEFAULT_BROADCASTER_HOST = 'localhost'
DEFAULT_BROADCASTER_PORT = 8081

DEFAULT_LOG_FILENAME = '/var/log/yadtreceiver.log'
DEFAULT_PYTHON_COMMAND = '/usr/bin/python'
DEFAULT_SCRIPT_TO_EXECUTE = '/usr/bin/yadtshell'
DEFAULT_TARGETS = set()
DEFAULT_TARGETS_DIRECTORY = '/etc/yadtshell/targets/'

SECTION_BROADCASTER = 'broadcaster'
SECTION_RECEIVER = 'receiver'


class ReceiverConfigLoader (object):

    """
        uses a YadtConfigParser which offers convenience methods.
    """

    def __init__(self):
        """
            Creates instance of YadtConfigParser which will be used to parse
            the configuration file.
        """
        self._parser = YadtConfigParser()

    def get_broadcaster_host(self):
        """
            @return: the broadcaster host from the configuration file,
                     otherwise DEFAULT_BROADCASTER_HOST.
        """
        return self._parser.get_option(SECTION_BROADCASTER, 'host', DEFAULT_BROADCASTER_HOST)

    def get_broadcaster_port(self):
        """
            @return: the broadcaster port from the configuration file as int,
                     otherwise DEFAULT_BROADCASTER_PORT.
        """
        return self._parser.get_option_as_int(SECTION_BROADCASTER, 'port', DEFAULT_BROADCASTER_PORT)

    def get_hostname(self):
        """
            @return: if a hostname is given in the configration file it will
                     return it, otherwise it will return the host name as
                     given by socket.gethostname
        """
        return self._parser.get_option(SECTION_RECEIVER, 'hostname', socket.gethostname())

    def get_log_filename(self):
        """
            @return: the log filename from the configuration file if given,
                     otherwise DEFAULT_LOG_FILENAME
        """
        return self._parser.get_option(SECTION_RECEIVER, 'log_filename', DEFAULT_LOG_FILENAME)

    def get_python_command(self):
        """
            @return: the python command from the configuration file if given,
                     otherwise DEFAULT_PYTHON_COMMAND
        """
        return self._parser.get_option(SECTION_RECEIVER, 'python_command', DEFAULT_PYTHON_COMMAND)

    def get_script_to_execute(self):
        """
            @return: if the configuration file provides a script to execute,
                     otherwise DEFAULT_SCRIPT_TO_EXECUTE.
        """
        return self._parser.get_option(SECTION_RECEIVER, 'script_to_execute', DEFAULT_SCRIPT_TO_EXECUTE)

    def get_targets(self):
        """
            @return: the set of targets given in the configuration file,
                     otherwise DEFAULT_TARGETS.
        """
        return self._parser.get_option_as_set(SECTION_RECEIVER, 'targets', DEFAULT_TARGETS)

    def get_targets_directory(self):
        """
            @return: the targets directory from the configuration file,
                     otherwise DEFAULT_TARGETS_DIRECTORY.
        """
        return self._parser.get_option(SECTION_RECEIVER, 'targets_directory', DEFAULT_TARGETS_DIRECTORY)

    def read_configuration_file(self, filename):
        """
            Reads the given configuration file. Uses the YadtConfigParser.

            @return: configuration dictionary
        """
        return self._parser.read_configuration_file(filename)


class ReceiverConfig(object):

    def __init__(self, config_filename):
        self.config_filename = config_filename
        self.load()

    def load(self):
        parser = ReceiverConfigLoader()
        parser.read_configuration_file(self.config_filename)

        self.configuration = {
            'broadcaster_host': parser.get_broadcaster_host(),
            'broadcaster_port': parser.get_broadcaster_port(),
            'hostname': parser.get_hostname(),
            'log_filename': parser.get_log_filename(),
            'python_command': parser.get_python_command(),
            'script_to_execute': parser.get_script_to_execute(),
            'targets': parser.get_targets(),
            'targets_directory': parser.get_targets_directory()
        }
        self.compute_allowed_targets()

    def compute_allowed_targets(self):
        allowed_targets = []
        for target_glob in self['targets']:
            new_allowed_targets = glob(
                os.path.join(self['targets_directory'], target_glob))
            allowed_targets.extend(new_allowed_targets)
        self.configuration['allowed_targets'] = allowed_targets

    def reload_targets(self):
        parser = ReceiverConfigLoader()
        parser.read_configuration_file(self.config_filename)
        self.configuration['targets'] = parser.get_targets()
        self.compute_allowed_targets()

    def __getitem__(self, key):
        return self.configuration[key]

    def get(self, key, default=None):
        result = self.configuration[key]
        if result:
            return result
        else:
            return default


def load(filename):
    """
        loads configuration from a file.

        @return: Configuration object containing the data from the file.
    """

    return ReceiverConfig(filename)
