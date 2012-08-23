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

from yadtreceiver.graphite import send_update_notification_to_graphite

class GraphiteTests(unittest.TestCase):
    @patch('yadtreceiver.graphite.time')
    @patch('yadtreceiver.graphite.socket')
    def test_should_send_update_message_to_graphite (self, mock_socket, mock_time):
        mock_time.return_value = 1
        mock_graphite_socket = Mock()
        mock_socket.return_value = mock_graphite_socket

        send_update_notification_to_graphite('target', 'host', 123)

        self.assertEquals(call(), mock_socket.call_args)
        self.assertEquals(call(('host', 123)), mock_graphite_socket.connect.call_args)
        self.assertEquals(call('yadt.target.update 1 1\n'), mock_graphite_socket.send.call_args)
        self.assertEquals(call(), mock_graphite_socket.close.call_args)


    @patch('yadtreceiver.graphite.log')
    @patch('yadtreceiver.graphite.time')
    @patch('yadtreceiver.graphite.socket')
    def test_should_close_socket_even_when_error_occurs (self, mock_socket, mock_time, mock_log):
        mock_time.return_value = 1
        mock_graphite_socket = Mock()
        mock_graphite_socket.connect.side_effect = Exception('Oh no.')
        mock_socket.return_value = mock_graphite_socket

        send_update_notification_to_graphite('target', 'host', 123)

        self.assertEquals(call(), mock_socket.call_args)
        self.assertEquals(call(('host', 123)), mock_graphite_socket.connect.call_args)
        self.assertEquals(call(), mock_graphite_socket.close.call_args)

