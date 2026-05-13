from abc import ABC, abstractmethod

class BaseReviewer(ABC):

    @abstractmethod
    def review_code(self, file_patch: list):
        pass