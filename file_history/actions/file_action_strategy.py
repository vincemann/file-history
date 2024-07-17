from abc import ABC, abstractmethod


# strategy for performing an action on a selected file
class FileActionStrategy(ABC):
    @abstractmethod
    def perform(self, file_path: str) -> None:
        pass
