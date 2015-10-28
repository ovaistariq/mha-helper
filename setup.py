# (c) 2015, Ovais Tariq <me@ovaistariq.net>
#
# This file is part of mha_helper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# To workaround hard link error
# http://stackoverflow.com/questions/7719380/python-setup-py-sdist-error-operation-not-permitted
# http://bugs.python.org/issue8876#msg208792
import os
del os.link

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import mha_helper


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

longdesc = '''
MHA helper is a Python module that supplements in doing proper failover using MHA_.
MHA is responsible for executing the important failover steps such as finding the
most recent slave to failover to, applying differential logs, monitoring master for
failure, etc. But it does not deal with additional steps that need to be taken
before and after failover. These would include steps such as setting the read-only
flag, killing connections, moving writer virtual IP, etc.

Required packages:
    PyMySQL
    paramiko

.. _MHA: https://code.google.com/p/mysql-master-ha/
'''

setup(
    name=mha_helper.__name__,
    version=mha_helper.__version__,
    description="A Python module that supplements MHA in doing proper MySQL master failover",
    long_description=longdesc,
    author=mha_helper.__author__,
    author_email=mha_helper.__email__,
    url=mha_helper.__url__,
    license="GNU GENERAL PUBLIC LICENSE Version 3",
    packages=['mha_helper'],
    scripts=['scripts/master_failover_report',
             'scripts/master_ip_hard_failover_helper',
             'scripts/master_ip_online_failover_helper',
             'scripts/mysql_failover',
             'scripts/mysql_online_failover'],
    install_requires=['PyMySQL>=0.6.3',
                      'paramiko>=1.10.0'],
    keywords='mha_helper, mha, mysql, failover, high availability',
    classifiers=[
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU GPL Version 3',
        'Environment :: Console',
        'Topic :: Database',
        'Natural Language :: English'
    ]
)
