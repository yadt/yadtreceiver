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

__author__ = 'Arne Hilmann, Michael Gruber'

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


class EventValidationException(Exception):
    """
        to be raised when an error during validation of an event occurs.
    """

class Event (object):

    def __init__(self, target, data):
        self.target = target
        self._event_type = data[ATTRIBUTE_TYPE]

        if self.is_a_request:
            if not ATTRIBUTE_COMMAND in data:
                raise EventValidationException('Request is missing attribute "{0}", got {1}.'.format(ATTRIBUTE_COMMAND, data))

            self.command = data[ATTRIBUTE_COMMAND]
            self.arguments = data[ATTRIBUTE_ARGUMENTS]

        if self.is_a_service_change:
            payload = data[ATTRIBUTE_PAYLOAD][0]

            self.service = payload[PAYLOAD_ATTRIBUTE_URI]
            self.state = payload[PAYLOAD_ATTRIBUTE_STATE]

        if self.is_a_command:
            self.state = data[ATTRIBUTE_STATE]
            self.command = data[ATTRIBUTE_COMMAND]

            if ATTRIBUTE_MESSAGE in data:
                self.message = data[ATTRIBUTE_MESSAGE]

    @property
    def is_a_request(self):
        return self._event_type == TYPE_REQUEST

    @property
    def is_a_full_update(self):
        return self._event_type == TYPE_FULL_UPDATE

    @property
    def is_a_service_change(self):
        return self._event_type == TYPE_SERVICE_CHANGE

    @property
    def is_a_command(self):
        return self._event_type == TYPE_COMMAND

    def __str__(self):
        if self.is_a_request:
            return 'target[{0}] requested command "{1}" using arguments "{2}"'.format(self.target, self.command, self.arguments)

        if self.is_a_full_update:
            return 'target[{0}] full update of status information.'.format(self.target)

        if self.is_a_service_change:
            return 'target[{0}] change: {1} is {2}'.format(self.target, self.service, self.state)

        if self.is_a_command:
            if hasattr(self, 'message'):
                return '(broadcaster) target[{0}] command "{1}" {2}: {3}'.format(self.target, self.command, self.state, self.message)
            else:
                return '(broadcaster) target[{0}] command "{1}" {2}.'.format(self.target, self.command, self.state)

        raise NotImplementedError('Unknown event type {0}'.format(self._event_type))
