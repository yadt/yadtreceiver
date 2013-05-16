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
    Provides the ProcessProtocol.
"""

__author__ = 'Michael Gruber, Maximilien Riehl'

from twisted.internet import protocol
from twisted.python import log

from yadtreceiver import events

try: # pragma: no cover
    import cStringIO
    StringIO = cStringIO
except: # pragma: no cover
    import StringIO


class ProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, hostname, broadcaster, target, readable_command, tracking_id=None):
        """
            Initializes the process protocol with the given properties.
        """
        self.broadcaster = broadcaster
        self.hostname = hostname
        self.readable_command = readable_command
        self.target = target
        self.tracking_id = tracking_id
        self.error_buffer = StringIO.StringIO()

        log.msg('(%s) target[%s] executing "%s"' % (self.hostname, target, readable_command))


    def processExited(self, reason):
        """
            publishes a finished-event when exit code of the execution is 0
            otherwise publishes a failed-event.
        """
        return_code = reason.value.exitCode

        if return_code != 0:
            self.publish_failed(return_code)
            return

        self.publish_finished()


    def publish_finished(self):
        """
            Uses the broadcaster-client to publish a finished-event.
        """
        message = '(%s) target[%s] request finished: "%s" succeeded.' \
                  % (self.hostname, self.target, self.readable_command)
        log.msg(message)
        self.error_buffer.close()
        self.broadcaster.publish_cmd_for_target(self.target, self.readable_command, events.FINISHED,
                                                message, tracking_id=self.tracking_id)


    def publish_failed(self, return_code):
        """
            Uses the broadcaster-client to publish a failed-event.
            The given return code will be included into the message of the event.
        """
        error_output = self.error_buffer.getvalue()
        self.error_buffer.close()
        error_message = '(%s) target[%s] request "%s" failed: return code was %s.' \
                        % (self.hostname, self.target, self.readable_command, return_code)
        log.err(error_message)
        self.broadcaster.publish_cmd_for_target(self.target, self.readable_command, events.FAILED,
                                                message=error_output, tracking_id=self.tracking_id)

    def errReceived(self, data):
        self.error_buffer.write(str(data))

