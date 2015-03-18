name              "mysql-mha"
maintainer        "Ovais Tariq"
maintainer_email  "me@ovaistariq.net"
description       "Setup and configure MHA manager, node packages and mha-helper (https://github.com/ovaistariq/mha-helper)"
long_description  "Please refer to README.md"
version           "0.1.0"
license           "All rights reserved"

recipe "mysql-mha",            "Performs common operations that are common to both MHA manager and node machines"
recipe "mysql-mha::node",      "Configures a MHA node machine"
recipe "mysql-mha::manager",   "Configures a MHA manager machine"

depends "yum-epel"

supports "centos"
supports "redhat"