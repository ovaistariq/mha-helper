=================================
MHA Helper Integration Test Suite
=================================

Bundler
-------
A ruby environment with Bundler installed is a prerequisite for using
this testing harness. At the time of this writing, it works with
Ruby >= 1.9.3 and Bundler >= 1.5.3. All programs involved, with the
exception of Vagrant, can be installed by cd'ing into the "tests/integration"
directory of this repository and running "bundle install" as shown
below.

::

  $ sudo gem install bundler
  $ cd tests/integration
  $ bundle install --binstubs --path .bundle


Rakefile
--------
The Rakefile ships with a number of tasks, each of which can be ran
individually, or in groups. Typing "rake" by itself will perform
integration with Test Kitchen using the Vagrant driver by
default. Alternatively, integration tests can be ran with Test Kitchen
EC2 driver.

::

  $ ./bin/rake -T
  rake cleanup                     # Clean up generated files
  rake cleanup:kitchen_destroy     # Destroy test-kitchen instances
  rake integration                 # Run full integration
  rake integration:vagrant_setup   # Setup the test-kitchen vagrant instances
  rake integration:vagrant_verify  # Verify the test-kitchen vagrant instances
  rake setup                       # Generate the setup

Integration Testing
-------------------
Integration testing is performed by Test Kitchen. Test Kitchen will
use the Vagrant driver to instantiate machines and apply Chef cookbooks.
After a successful converge, tests are uploaded and ran out of band of Chef.

Integration Testing using Vagrant
---------------------------------
Integration tests can be performed on a local workstation using
Virtualbox or VMWare. Detailed instructions for setting this up can be
found at the [Bento](https://github.com/chef/bento) project web site.

Integration tests using Vagrant can be performed with

::

  ./bin/rake integration
