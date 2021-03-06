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
from pybuilder.core import use_plugin, init, Author

use_plugin('filter_resources')

use_plugin('python.core')
use_plugin('python.coverage')
use_plugin('python.unittest')
use_plugin('python.integrationtest')
use_plugin('python.install_dependencies')
use_plugin('python.distutils')
use_plugin('python.pydev')
use_plugin('copy_resources')

use_plugin('python.flake8')
use_plugin('python.sonarqube')

authors = [Author('Arne Hilmann', 'arne.hilmann@gmail.com'),
           Author('Maximilien Riehl', 'maximilien.riehl@gmail.com'),
           Author('Michael Gruber', 'aelgru@gmail.com')]
license = 'GNU GPL v3'
name = 'yadtreceiver'
summary = 'Executes yadtshell commands triggered by a yadtbroadcaster.'
url = 'https://github.com/yadt/yadtreceiver'
version = '0.4.1'

default_task = ['analyze', 'publish']


@init
def set_properties(project):
    project.depends_on('PyYAML')
    project.depends_on('Twisted')
    project.depends_on('psutil')
    project.depends_on('yadtcommons')
    project.depends_on('yadtbroadcast-client-wamp2')
    project.depends_on('fysom')

    project.build_depends_on('mock')
    project.build_depends_on('coverage')

    project.set_property('verbose', True)

    project.set_property('coverage_break_build', True)
    project.set_property('coverage_threshold_warn', 85)

    project.set_property('install_dependencies_upgrade', True)

    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('filter_resources_glob').append('**/yadtreceiver/__init__.py')
    project.get_property('copy_resources_glob').append('setup.cfg')
    project.get_property('copy_resources_glob').append('post-install.sh')
    project.get_property('copy_resources_glob').append('post-uninstall.sh')
    project.set_property('dir_dist_scripts', 'scripts')

    project.install_file('/etc/twisted-taps/', 'yadtreceiver/yadtreceiver.tac')
    project.install_file('/etc/init.d/', 'yadtreceiver/yadtreceiver')


@init(environments="teamcity")
def set_properties_for_teamcity(project):
    import os
    project.version = '%s-%s' % (project.version, os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['install_build_dependencies', 'analyze', 'package', 'run_sonar_analysis']
    project.get_property('distutils_commands').append('bdist_rpm')
    project.set_property('teamcity_output', True)
