import docker

def main(self):
    pass

class TestNetwork():
    def __init__(self, topology, ) -> None:
        self.containerList

        pass

    def run(self):
        pass

    def pause(self):
        for i in range(len(self.containerList)):
            self.containerList[i].pause()

    def unpause(self):
        pass

    def runTest(self, host):
        pass

    def availableTests(self):
        pass

    def info(self):
        pass

    def kill(self):
        pass

    def logs(self):
        pass

    def restart(self):
        pass




client = docker.DockerClient(base_url='tcp://127.0.0.1:2376')

client.containers.run("ubuntu", "echo hello world")
client.containers.list()
client.images.pull('nginx')
