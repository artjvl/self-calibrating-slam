from abc import ABC

from src.simulation.results.Results import Results


class ResultsPlain(Results, ABC):
    def configure(self) -> None:
        super().configure()
        self.set_plain_simulation()

    def loop(self, iteration: int) -> None:
        pass

    def finalise(self) -> None:
        pass
