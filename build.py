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

from pythonbuilder.core import use_plugin, init, Author

use_plugin('filter_resources')

use_plugin('python.core')
use_plugin('python.coverage')
use_plugin('python.unittest')
use_plugin('python.integrationtest')
use_plugin('python.distutils')
use_plugin('python.pep8')
use_plugin('python.pydev')

authors = [Author('Arne Hilmann', 'arne.hilmann@gmail.com'),
           Author('Michael Gruber', 'aelgru@gmail.com')]
license = 'GNU GPL v3'
summary = 'yadtreceiver'
url     = 'https://github.com/yadt/yadtreceiver'
version = '0.1.7'

default_task = ['analyze', 'publish']

@init
def set_properties (project):
    project.set_property('coverage_break_build', False)
    project.set_property('pychecker_break_build', False)
    project.set_property('pep8_break_build', True)
    project.get_property('distutils_commands').append('bdist_rpm')

    project.get_property('filter_resources_glob').append('**/yadtreceiver/__init__.py')

    project.install_file('/etc/twisted-taps/', 'yadtreceiver/yadtreceiver.tac')
    project.install_file('/etc/init.d/', 'yadtreceiver/yadtreceiver')
