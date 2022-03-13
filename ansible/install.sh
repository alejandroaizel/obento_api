#!/bin/bash

os=$1

if [ "$os" = "linux" ]; then
    echo "[OS: LINUX]"
    echo "Instalando Python..."
    apt-get update
    apt-get install -y python

    echo "Instalando Ansible..."
    apt-get install -y software-properties-common
    apt-add-repository --yes --update ppa:ansible/ansible
    apt-get install -y ansible

elif [ "$os" = "macos" ]; then
    echo "[OS: MACOS]"
    echo "Instalando Python..."
    brew update
    brew install python

    echo "Instalando Ansible..."
    brew install ansible
else
    echo "OS $os not supported"
fi
