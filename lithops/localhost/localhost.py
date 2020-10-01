#
# Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import json
import lithops
import logging
import shutil
import subprocess
from shutil import copyfile

from lithops.localhost.environments import DefaultEnv, VirtualEnv, DockerEnv
from lithops.config import TEMP, STORAGE_DIR, JOBS_PREFIX


logger = logging.getLogger(__name__)
LOCAL_HANDLER_NAME = 'local_handler.py'
HANDLER_FILE = os.path.join(STORAGE_DIR, LOCAL_HANDLER_NAME)
LITHOPS_LOCATION = os.path.dirname(os.path.abspath(lithops.__file__))


class LocalhostHandler:
    """
    A localhostHandler object is used by invokers and other components to access
    underlying localhost backend without exposing the implementation details.
    """

    def __init__(self, localhost_config):
        self.config = localhost_config
        self.runtime = self.config['runtime']

        if self.runtime is None:
            self.env = DefaultEnv()
            self.env_type = 'default'
        else:
            self.env = DockerEnv(self.runtime)
            self.env_type = 'docker'

    def run_job(self, job_payload):
        """
        Run the job description agains the selected environemnt
        """
        runtime = job_payload['job_description']['runtime_name']
        exec_command = self.env.get_execution_cmd(runtime)

        executor_id = job_payload['executor_id']
        job_id = job_payload['job_id']
        storage_bucket = job_payload['config']['lithops']['storage_bucket']

        job_dir = os.path.join(STORAGE_DIR, storage_bucket,
                               JOBS_PREFIX, executor_id, job_id)
        os.makedirs(job_dir, exist_ok=True)
        jobr_filename = os.path.join(job_dir, 'job.json')

        with open(jobr_filename, 'w') as jl:
            json.dump(job_payload, jl)

        log_file = open(os.path.join(STORAGE_DIR, 'local_handler.log'), 'a')
        subprocess.Popen(exec_command+' run '+jobr_filename, shell=True,
                         stdout=log_file, universal_newlines=True)

    def create_runtime(self, runtime):
        """
        Extract the runtime metadata and preinstalled modules
        """
        self.env.setup()
        exec_command = self.env.get_execution_cmd(runtime)
        process = subprocess.run(exec_command+' modules', shell=True, check=True,
                                 stdout=subprocess.PIPE, universal_newlines=True)
        runtime_meta = json.loads(process.stdout.strip())

        return runtime_meta

    def get_runtime_key(self, runtime_name):
        """
        Generate the runtime key that identifies the runtime
        """
        runtime_key = os.path.join('localhost', self.env_type, runtime_name.strip("/"))

        return runtime_key


class DockerEnv:
    def __init__(self, docker_image):
        self.runtime = docker_image

    def setup(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        shutil.copytree(LITHOPS_LOCATION, os.path.join(STORAGE_DIR, 'lithops'))
        src_handler = os.path.join(LITHOPS_LOCATION, 'localhost', LOCAL_HANDLER_NAME)
        copyfile(src_handler, HANDLER_FILE)

    def get_execution_cmd(self, docker_image_name):
        p = subprocess.run("id -u $USER", shell=True,
                           check=True, stdout=subprocess.PIPE)
        uid = int(p.stdout.strip())

        cmd = ('docker run --user {} --rm -v {}:/tmp --entrypoint "python" {} {}'
               .format(uid, TEMP, docker_image_name, HANDLER_FILE))

        return cmd


class DefaultEnv:
    def __init__(self):
        self.runtime = sys.executable

    def setup(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        src_handler = os.path.join(LITHOPS_LOCATION, 'localhost', LOCAL_HANDLER_NAME)
        copyfile(src_handler, HANDLER_FILE)

    def get_execution_cmd(self, runtime):
        cmd = '{} {}'.format(self.runtime, HANDLER_FILE)
        return cmd
