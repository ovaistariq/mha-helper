#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='mha_helper',
    version='0.4.0',
    description=("MHA helper (mha-helper) is a set of helper scripts that supplement in doing proper failover using "
                 "MHA (https://code.google.com/p/mysql-master-ha/). MHA is responsible for executing the important "
                 "failover steps such as finding the most recent slave to failover to, applying differential logs, "
                 "monitoring master for failure, etc. But it does not deal with additional steps that need to be taken "
                 "before and after failover. These would include steps such as setting the read-only flag, "
                 "killing connections, moving writer virtual IP, etc. Furthermore, the monitor that does the "
                 "monitoring of masters to test for failure is not daemonized and exits after performing the failover "
                 "which might not be intended, because of course we need the monitor to keep monitoring even after "
                 "failover."),
    long_description=readme + '\n\n' + history,
    author="Ovais Tariq",
    author_email='me@ovaistariq.net',
    url='https://github.com/ovaistariq/mha-helper',
    packages=[
        'mha_helper',
    ],
    package_dir={'mha_helper':
                 'mha_helper'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='mha_helper, mha',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
