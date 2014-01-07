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

from yadtreceiver.events import (Event,
                                 IncompleteEventDataException,
                                 PayloadIntegrityException,
                                 InvalidEventTypeException)


class EventTests(TestCase):

    def test_should_raise_exception_when_payload_attribute_is_missing_in_vote(self):
        self.assertRaises(IncompleteEventDataException,
                          Event, 'target-name', {'id': 'vote'})

    def test_should_raise_exception_when_command_attribute_is_missing_in_request(self):
        self.assertRaises(IncompleteEventDataException, Event,
                          'target-name', {'id': 'request', 'args': 'arg1 arg2 arg3'})

    def test_should_raise_exception_when_type_attribute_is_missing_in_request(self):
        self.assertRaises(InvalidEventTypeException, Event, 'target-name', {})

    def test_should_raise_exception_when_arguments_attribute_is_missing_in_request(self):
        self.assertRaises(IncompleteEventDataException, Event,
                          'target-name', {'id': 'request', 'cmd': 'command'})

    def test_should_raise_exception_when_command_attribute_is_missing_in_command(self):
        self.assertRaises(IncompleteEventDataException, Event,
                          'target-name', {'id': 'cmd', 'state': 'state'})

    def test_should_raise_exception_when_state_attribute_is_missing_in_command(self):
        self.assertRaises(IncompleteEventDataException, Event,
                          'target-name', {'id': 'cmd', 'cmd': 'command'})

    def test_should_raise_exception_when_payload_attribute_is_missing_in_service_change(self):
        self.assertRaises(IncompleteEventDataException,
                          Event, 'target-name', {'id': 'service-change'})

    def test_should_raise_exception_when_service_change_payload_contains_service_state_with_missing_uri(self):
        payload_with_no_uri_in_service_change = {'id': 'service-change',
                                                 'payload': [{'state': 'up'}]}
        self.assertRaises(PayloadIntegrityException, Event,
                          'target-name', payload_with_no_uri_in_service_change)

    def test_should_raise_exception_when_service_change_payload_contains_service_state_with_missing_state(self):
        payload_with_no_state_in_service_change = {'id': 'service-change',
                                                   'payload': [{'uri': 'spam'}]}
        self.assertRaises(PayloadIntegrityException, Event,
                          'target-name', payload_with_no_state_in_service_change)

    def test_should_raise_exception_when_event_type_unknown(self):
        invalid_event_data = {'id': 'spameggs'}
        self.assertRaises(
            InvalidEventTypeException, Event, 'target-name', invalid_event_data)

    def test_should_return_description_of_multiple_service_changes(self):
        event = Event('target-name', {'id': 'service-change',
                                      'payload': [{'uri': 'spam',
                                                   'state': 'up'},
                                                  {'uri': 'eggs',
                                                   'state': 'down'}]
                                      })
        self.assertEqual(
            str(event), 'target[target-name] services changed: spam is up, eggs is down')

    def test_should_not_complain_upon_instantiating_heartbeat_events(self):
        Event('target-name', {'id': 'heartbeat',
                              'type': 'event',
                              'target': 'dev12',
                              'tracking_id': None,
                              'payload': None})

    def test_should_return_description_of_request(self):
        event = Event('target-name', {'id': 'request',
                                      'cmd': 'command',
                                      'args': 'arg1 arg2 arg3'})

        self.assertEqual(
            'target[target-name] requested command "command" using arguments "arg1 arg2 arg3"', str(event))

    def test_should_return_description_of_vote(self):
        event = Event('target-name', {'id': 'vote',
                                      'payload': 42
                                      })

        self.assertEqual(
            'Vote with value 42', str(event))

    def test_should_return_description_of_error_info(self):
        event = Event('target-name', {'id': 'error-info',
                                      'target': 'foo'
                                      })

        self.assertEqual(
            'Error info from target target-name', str(event))

    def test_should_return_description_of_heartbeat(self):
        event = Event('target-name', {'id': 'heartbeat',
                                      'type': 'event',
                                      'target': 'target-name',
                                      'tracking_id': None,
                                      'payload': None})
        self.assertEqual('Heartbeat on target-name', str(event))

    def test_should_return_description_of_full_update(self):
        event = Event('target-name', {'id': 'full-update'})

        self.assertEqual(
            'target[target-name] full update of status information.', str(event))

    def test_should_return_description_of_a_service_change(self):
        event = Event('target-name', {'id': 'service-change',
                                      'payload': [{'uri': 'service://host/test-service',
                                                   'state': 'up'}]})

        self.assertEqual(
            'target[target-name] services changed: service://host/test-service is up', str(event))

    def test_should_return_description_of_command_with_message(self):
        event = Event('target-name', {'id': 'cmd',
                                      'cmd': 'command',
                                      'state': 'state',
                                      'message': 'message'})

        self.assertEqual(
            '(broadcaster) target[target-name] command "command" state: message', str(event))

    def test_should_return_description_of_command_without_message(self):
        event = Event('target-name', {'id': 'cmd',
                                      'cmd': 'command',
                                      'state': 'state'})

        self.assertEqual(
            '(broadcaster) target[target-name] command "command" state.', str(event))

    def test_should_return_description_of_command_when_message_is_none(self):
        event = Event('target-name', {'id': 'cmd',
                                      'cmd': 'command',
                                      'state': 'state',
                                      'message': None})

        self.assertEqual(
            '(broadcaster) target[target-name] command "command" state.', str(event))
