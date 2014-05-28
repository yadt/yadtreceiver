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

from StringIO import StringIO

from mock import Mock, call, patch

from yadtreceiver.protocols import ProcessProtocol
from yadtreceiver import METRICS


class ProcessProtocolTests (unittest.TestCase):

    def test_should_initialize_with_given_properties(self):
        mock_broadcaster = Mock()
        protocol = ProcessProtocol(
            'hostname', mock_broadcaster, 'devabc123', '/usr/bin/python abc 123', tracking_id='tracking-id')

        self.assertEquals('hostname', protocol.hostname)
        self.assertEquals(mock_broadcaster, protocol.broadcaster)
        self.assertEquals('devabc123', protocol.target)
        self.assertEquals('/usr/bin/python abc 123', protocol.readable_command)
        self.assertEqual('tracking-id', protocol.tracking_id)

    def test_should_publish_as_failed_event_when_return_code_not_zero(self):
        mock_reason = Mock()
        mock_reason.value.exitCode = 123
        mock_protocol = Mock(ProcessProtocol)

        ProcessProtocol.processExited(mock_protocol, mock_reason)

        self.assertEquals(call(123), mock_protocol.publish_failed.call_args)

    def test_should_publish_as_finished_event_when_return_code_is_zero(self):
        mock_reason = Mock()
        mock_reason.value.exitCode = 0
        mock_protocol = Mock(ProcessProtocol)

        ProcessProtocol.processExited(mock_protocol, mock_reason)

        self.assertEquals(call(), mock_protocol.publish_finished.call_args)

    @patch.dict('yadtreceiver.METRICS', {}, clear=True)
    def test_should_publish_finished_event(self):
        mock_protocol = Mock(ProcessProtocol)
        mock_broadcaster = Mock()
        mock_protocol.broadcaster = mock_broadcaster
        mock_protocol.hostname = 'hostname'
        mock_protocol.target = 'dev123'
        mock_protocol.readable_command = '/usr/bin/python abc'
        mock_protocol.tracking_id = 'tracking-id'
        mock_protocol.error_buffer = Mock()

        ProcessProtocol.publish_finished(mock_protocol)

        self.assertEquals(call('dev123', '/usr/bin/python abc', 'finished',
                          '(hostname) target[dev123] request finished: "/usr/bin/python abc" succeeded.', tracking_id='tracking-id'), mock_broadcaster.publish_cmd_for_target.call_args)
        self.assertEqual(METRICS['commands_succeeded.dev123'], 1)

    @patch('yadtreceiver.protocols.log')
    @patch.dict('yadtreceiver.METRICS', {}, clear=True)
    def test_should_publish_failed_event_with_stderr_from_process(self, mock_log):
        mock_protocol = Mock(ProcessProtocol)
        mock_broadcaster = Mock()
        mock_protocol.broadcaster = mock_broadcaster
        mock_protocol.hostname = 'hostname'
        mock_protocol.target = 'dev123'
        mock_protocol.readable_command = '/usr/bin/python abc'
        mock_protocol.tracking_id = 'tracking_id'
        mock_protocol.error_buffer = StringIO(
            'Someone has shut down the internet.')

        ProcessProtocol.publish_failed(mock_protocol, 123)

        self.assertEquals(call('dev123',
                               '/usr/bin/python abc',
                               'failed',
                               message='Someone has shut down the internet.',
                               tracking_id='tracking_id'),
                          mock_broadcaster.publish_cmd_for_target.call_args)
        self.assertEqual(METRICS['commands_failed.dev123'], 1)

    @patch('yadtreceiver.protocols.log')
    def test_should_accumulate_error_output(self, mock_log):
        mock_broadcaster = Mock()
        protocol = ProcessProtocol(
            'hostname', mock_broadcaster, 'devabc123', '/usr/bin/python abc 123', tracking_id='tracking-id')

        self.assertEqual(protocol.error_buffer.getvalue(), '')

        protocol.errReceived('foo\nbar')
        protocol.errReceived('baz')

        self.assertEqual('foo\nbarbaz', protocol.error_buffer.getvalue())
