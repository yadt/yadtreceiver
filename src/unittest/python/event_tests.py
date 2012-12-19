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


__author__ = 'Michael Gruber, Maximilien Riehl'

from unittest import TestCase

from yadtreceiver.events import Event, IncompleteEventDataException

class EventTests(TestCase):
    def test_should_raise_exception_when_command_attribute_is_missing_in_request(self):
        self.assertRaises(IncompleteEventDataException, Event, 'target-name', {'id': 'request','args': 'arg1 arg2 arg3'})


    def test_should_raise_exception_when_arguments_attribute_is_missing_in_request(self):
        self.assertRaises(IncompleteEventDataException, Event, 'target-name', {'id': 'request','cmd' : 'command'})

    def test_should_raise_exception_when_payload_attribute_is_missing_in_service_change(self):
        self.assertRaises(IncompleteEventDataException, Event, 'target-name', {'id': 'service-change'})

    def test_should_raise_exception_when_command_attribute_is_missing_in_command(self):
        self.assertRaises(IncompleteEventDataException, Event, 'target-name', {'id': 'cmd', 'state' : 'state'})

    def test_should_raise_exception_when_state_attribute_is_missing_in_command(self):
        self.assertRaises(IncompleteEventDataException, Event, 'target-name', {'id': 'cmd', 'cmd' : 'command'})

    def test_should_return_description_of_multiple_service_changes(self):
        event = Event('target-name', {'id'      : 'service-change',
                                      'payload' : [{'uri' : 'spam',
                                                    'state' : 'up'},
                                                   {'uri' : 'eggs',
                                                    'state' : 'down'}]
                                     })
        self.assertEqual(str(event), 'target[target-name] service changes: spam is up, eggs is down')

    def test_should_return_description_of_request(self):
        event = Event('target-name', {'id': 'request',
                                      'cmd': 'command',
                                      'args': 'arg1 arg2 arg3'})

        self.assertEqual('target[target-name] requested command "command" using arguments "arg1 arg2 arg3"', str(event))

    def test_should_return_description_of_full_update(self):
        event = Event('target-name', {'id': 'full-update'})

        self.assertEqual('target[target-name] full update of status information.', str(event))

    def test_should_return_description_of_a_service_change(self):
        event = Event('target-name', {'id': 'service-change',
                                      'payload': [{'uri': 'service://host/test-service',
                                                   'state': 'up'}]})

        self.assertEqual('target[target-name] service change: service://host/test-service is up', str(event))

    def test_should_return_description_of_command_with_message(self):
        event = Event('target-name', {'id': 'cmd',
                                      'cmd': 'command',
                                      'state': 'state',
                                      'message': 'message'})

        self.assertEqual('(broadcaster) target[target-name] command "command" state: message', str(event))

    def test_should_return_description_of_command_without_message(self):
        event = Event('target-name', {'id': 'cmd',
                                      'cmd': 'command',
                                      'state': 'state'})

        self.assertEqual('(broadcaster) target[target-name] command "command" state.', str(event))

    def test_should_return_description_of_command_when_message_is_none(self):
        event = Event('target-name', {'id': 'cmd',
                                      'cmd': 'command',
                                      'state': 'state',
                                      'message': None})

        self.assertEqual('(broadcaster) target[target-name] command "command" state.', str(event))
