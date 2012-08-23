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


__author__ = 'Michael Gruber'

import unittest

from mock import Mock, call, patch

from yadtreceiver.protocols import ProcessProtocol

class ProcessProtocolTests (unittest.TestCase):
    def test_should_initialize_with_given_properties (self):
        mock_broadcaster = Mock()
        protocol = ProcessProtocol('hostname', mock_broadcaster, 'devabc123', '/usr/bin/python abc 123')

        self.assertEquals('hostname', protocol.hostname)
        self.assertEquals(mock_broadcaster, protocol.broadcaster)
        self.assertEquals('devabc123', protocol.target)
        self.assertEquals('/usr/bin/python abc 123', protocol.readable_command)
