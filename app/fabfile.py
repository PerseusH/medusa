from fabric.api import *


env.user = "root"
env.password = "Hui(8091)"


env.hosts = ["47.100.40.116"]


def build(): pass


def deploy():
    run("mkdir /root/dir_from_fabric")
