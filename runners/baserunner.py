from abc import ABC, abstractmethod
from typing import List


class BaseRunner(ABC):
    def __init__(self, model_name: str, task_names: List[str] = None, device: str = "cuda",
                 batch_size: int = 16, max_length: int = 256):
        self.model_name = model_name
        self.task_names = task_names
        self.device = device
        self.batch_size = batch_size
        self.max_length = max_length
        self.progress = 0.0  # Initialize progress to 0.0 as a float

    @abstractmethod
    def generate_predictions(self):
        pass

    @abstractmethod
    def score_predictions(self):
        pass

    @abstractmethod
    def evaluate_predictions(self):
        pass

    @abstractmethod
    def get_generation_progress(self) -> float:
        pass

