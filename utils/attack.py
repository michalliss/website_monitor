import multiprocessing
from abc import ABC, abstractmethod
from time import sleep
from project.utils import slowloris


class Attack(ABC):
    @abstractmethod
    def run(self, webpage_url, timeout):
        pass


class SlowLorisAttack(Attack):
    @staticmethod
    def run_helper(webpage):
        slowloris.main(webpage, 600)

    def run(self, webpage_url, timeout):
        proc = multiprocessing.Process(target=self.run_helper, args=(webpage_url,))
        proc.start()
        sleep(timeout)
        proc.terminate()
