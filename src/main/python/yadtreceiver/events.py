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
    A broadcaster event.
"""

__author__ = 'Arne Hilmann, Michael Gruber, Maximilien Riehl'

FAILED = 'failed'
FINISHED = 'finished'
STARTED = 'started'

ATTRIBUTE_ARGUMENTS = 'args'
ATTRIBUTE_COMMAND = 'cmd'
ATTRIBUTE_MESSAGE = 'message'
ATTRIBUTE_STATE = 'state'
ATTRIBUTE_TYPE = 'id'
ATTRIBUTE_PAYLOAD = 'payload'

PAYLOAD_ATTRIBUTE_URI = 'uri'
PAYLOAD_ATTRIBUTE_STATE = 'state'

TYPE_COMMAND = 'cmd'
TYPE_FULL_UPDATE = 'full-update'
TYPE_REQUEST = 'request'
TYPE_SERVICE_CHANGE = 'service-change'
KNOWN_EVENT_TYPES = [TYPE_COMMAND, TYPE_FULL_UPDATE, TYPE_REQUEST, TYPE_SERVICE_CHANGE]


class IncompleteEventDataException(Exception):
    """
        to be raised when an error during validation of an event occurs.
    """

    def __init__(self, event, attribute_name):
        error_message = 'Event "{1}" on target {0} is missing attribute "{2}", event dump : {3}'.format(event.target,
                                                                                            event.event_type,
                                                                                            attribute_name,
                                                                                            event.data)
        super(IncompleteEventDataException, self).__init__(error_message)

class InvalidEventTypeException(Exception):
    """
        to be raised when an invalid event is instantiated
    """
    def __init__(self, event, event_type):
        error_message = 'Event "{1}" on target {0} has invalid type, event dump : {2}'.format(event.target,
                                                                             event_type,
                                                                             event.data)
        super(InvalidEventTypeException, self).__init__(error_message)

class PayloadIntegrityException(Exception):
    """
        to be raised when a payload cannot be validated
    """

    def __init__(self, event, payload_attribute_name):
        error_message = 'Event "{1}" on target {0} is missing attribute {2} in payload, event dump : {3}'.format(
                                                                                               event.target,
                                                                                               event.event_type,
                                                                                               payload_attribute_name,
                                                                                               event.data)
        super(PayloadIntegrityException, self).__init__(error_message)

class Event (object):

    def __init__(self, target, data):
        self.target = target
        self.data = data
        self.event_type = self._ensure_is_valid_event_type()

        if self.is_a_request:
            self._initialize_request()

        if self.is_a_service_change:
            self._initialize_service_change()

        if self.is_a_command:
            self._initialize_command()

    def _initialize_request(self):
        self.command = self._ensure_attribute_in_data(ATTRIBUTE_COMMAND)
        self.arguments = self._ensure_attribute_in_data(ATTRIBUTE_ARGUMENTS)

    def _initialize_command(self):
        self.command = self._ensure_attribute_in_data(ATTRIBUTE_COMMAND)
        self.state = self._ensure_attribute_in_data(ATTRIBUTE_STATE)

        if ATTRIBUTE_MESSAGE in self.data:
            self.message = self.data[ATTRIBUTE_MESSAGE]

    def _initialize_service_change(self):
        payload = self._ensure_attribute_in_data(ATTRIBUTE_PAYLOAD)

        self.service_states = self._extract_service_states_from_payload(payload)

    def _extract_service_states_from_payload(self, payload):
        service_states = []

        for payload_entry in payload:
            uri = self._ensure_payload_entry_contains_attribute(payload_entry, PAYLOAD_ATTRIBUTE_URI)
            state = self._ensure_payload_entry_contains_attribute(payload_entry, PAYLOAD_ATTRIBUTE_STATE)
            service_states.append(self.ServiceState(uri, state))
        return service_states

    def _ensure_payload_entry_contains_attribute(self, payload_entry, attribute_name):
        if not attribute_name in payload_entry:
            raise PayloadIntegrityException(self, attribute_name)
        return payload_entry[attribute_name]

    def _ensure_is_valid_event_type(self):
        if ATTRIBUTE_TYPE not in self.data:
            raise InvalidEventTypeException(self, None)

        event_type = self.data[ATTRIBUTE_TYPE]
        if not event_type in KNOWN_EVENT_TYPES:
            raise InvalidEventTypeException(self, event_type)
        return event_type

    def _ensure_attribute_in_data(self, attribute_name):
        if not attribute_name in self.data:
            raise IncompleteEventDataException(self, attribute_name)
        return self.data[attribute_name]

    @property
    def is_a_request(self):
        return self.event_type == TYPE_REQUEST

    @property
    def is_a_full_update(self):
        return self.event_type == TYPE_FULL_UPDATE

    @property
    def is_a_service_change(self):
        return self.event_type == TYPE_SERVICE_CHANGE

    @property
    def is_a_command(self):
        return self.event_type == TYPE_COMMAND

    def __str__(self):
        if self.is_a_request:
            return 'target[{0}] requested command "{1}" using arguments "{2}"'.format(self.target, self.command, self.arguments)

        if self.is_a_full_update:
            return 'target[{0}] full update of status information.'.format(self.target)

        if self.is_a_service_change:
            state_changes = ', '.join(map(str, self.service_states))
            return 'target[{0}] services changed: {1}'.format(self.target, state_changes)

        if self.is_a_command:
            if hasattr(self, 'message') and self.message is not None:
                return '(broadcaster) target[{0}] command "{1}" {2}: {3}'.format(self.target, self.command, self.state, self.message)
            else:
                return '(broadcaster) target[{0}] command "{1}" {2}.'.format(self.target, self.command, self.state)

        raise NotImplementedError('Unknown event type {0}'.format(self.event_type))

    class ServiceState (object):
        def __init__(self, uri, state):
            self.uri = uri
            self.state = state

        def __str__(self):
            return '{0} is {1}'.format(self.uri, self.state)