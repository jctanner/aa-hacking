#!/usr/bin/env python3

import argparse
import copy
import getpass
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import platform
import yaml
import ruamel.yaml
from ruamel.yaml import YAML

from logzero import logger
from pprint import pprint



class CRCBuilder:

    BIN_DIR = os.path.abspath('srv/bin')

    CRC_TAR = os.path.expanduser('~/Downloads/crc-linux-amd64.tar.xz')
    CRC_TAR_BN = 'crc-linux-1.19.0-amd64'
    CRC_BIN = os.path.abspath('srv/bin/crc')
    PULL_SECRET = os.path.expanduser('~/Downloads/pull-secret.txt')

    OC_BIN = None

    def __init__(self, args=None):
        self.args = args
        self.verify_files()
        self.extract_files()
        self.start_crc()
        self.oc_env
        self.crc_credentials

    def verify_files(self):
        for x in [self.CRC_TAR, self.PULL_SECRET]:
            logger.info(f'checking {x}')
            if not os.path.exists(x):
                raise Exception(f'{x} is missing, please download it')

    def extract_files(self):
        if not os.path.exists(self.BIN_DIR):
            os.makedirs(self.BIN_DIR)

        if not os.path.exists(self.CRC_BIN):

            cmd = f'tar xvf {self.CRC_TAR}'
            logger.info(cmd)
            res = subprocess.run(cmd, cwd='/tmp', shell=True)
            if res.returncode != 0:
                raise Exception('extraction failed')

            shutil.copy(os.path.join('/tmp', self.CRC_TAR_BN, 'crc'), self.CRC_BIN)
            shutil.rmtree(os.path.join('/tmp', self.CRC_TAR_BN))
  
    @property
    def crc_running(self):
        cmd = f'{self.CRC_BIN} status'
        logger.info(cmd)
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        if res.returncode == 0:
            return True
        return False

    @property
    def oc_env(self):
        cmd = f'{self.CRC_BIN} oc-env'
        logger.info(cmd)
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        stdout = res.stdout.decode('utf-8')
        stdout = [x.strip() for x in stdout.split('\n') if not x.startswith('#') and x.strip()]
        if res.returncode == 0:
            stdout = res.stdout.decode('utf-8')
            stdout = [x.strip() for x in stdout.split('\n') if not x.startswith('#') and x.strip()]
            return stdout[0]
        return None

    @property
    def crc_credentials(self):
        cmd = f'{self.CRC_BIN} console --credentials'
        logger.info(cmd)
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        stdout = res.stdout.decode('utf-8')
        stdout = stdout.split('\n')

        creds = {}
        for line in stdout:
            # To login as an admin, run 'oc login -u kubeadmin -p hxYtC-KLeQC-kfNkm-ppi8i
            if not line.startswith('To login as'):
                continue

            username = None
            password = None
            words = line.split()
            for idx,x in enumerate(words):
                if x == '-u':
                    username = words[idx+1]
                elif x == '-p':
                    password = words[idx+1]

            creds[username] = password

        return creds

    def start_crc(self):
        if not self.crc_running:
            cleanup_cmd = f'{self.CRC_BIN} cleanup'
            logger.info(cleanup_cmd)
            res = subprocess.run(cleanup_cmd, shell=True)
            if res.returncode != 0:
                raise Exception('cleanup failed')

            delete_cmd = f'{self.CRC_BIN} delete'
            logger.info(delete_cmd)
            res = subprocess.run(delete_cmd, shell=True)
            #if res.returncode != 0:
            #    raise Exception('delete failed')

            setup_cmd = f'{self.CRC_BIN} setup'
            logger.info(setup_cmd)
            res = subprocess.run(setup_cmd, shell=True)
            if res.returncode != 0:
                raise Exception('setup failed')

            mem_cmd = f'{self.CRC_BIN} config set memory 16384'
            logger.info(mem_cmd)
            res = subprocess.run(mem_cmd, shell=True)
            if res.returncode != 0:
                raise Exception('memory config failed')

            start_cmd = f'{self.CRC_BIN} start --pull-secret-file={self.PULL_SECRET} --disk-size=50'
            logger.info(start_cmd)
            res = subprocess.run(start_cmd, shell=True)
            if res.returncode != 0:
                raise Exception('failed')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('operation', help=['what to do'], choices=['start', 'clean'])
    args = parser.parse_args()
    logger.info("starting cloudbuilder")
    cbuilder = CRCBuilder(args=args)


if __name__ == "__main__":
    main()
