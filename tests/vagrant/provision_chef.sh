#!/bin/bash

CHEF_VERSION=$1

if [[ -z ${CHEF_VERSION} ]]; then
  CHEF_VERSION="11.16.4"
fi

function chef_install() {
  curl -L https://www.chef.io/chef/install.sh | sudo bash -s -- -v ${CHEF_VERSION}
  
  if [ $? -ne 0 ]; then
    echo "Chef ${CHEF_VERSION} version not found"
  fi
}

function chef_uninstall() {
  sudo rpm -ef chef
}

if [ -f /usr/bin/chef-client ]; then
  CHEF_NODE_VERSION=$(rpm -q chef --info | grep Version | awk '{print $3}')

  if [ $CHEF_VERSION != $CHEF_NODE_VERSION ]; then
    echo "Removing chef $CHEF_NODE_VERSION"
    chef_uninstall
    echo "Installing chef-client $CHEF_VERSION"
    chef_install
  else
    echo "Chef $CHEF_VERSION is already installed..."
  fi
else
  echo "Chef is not installed. Installing ${CHEF_VERSION}..."
  chef_install
fi
