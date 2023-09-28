from abc import ABC, abstractmethod
from typing import List
import uuid


class BaseRunner(ABC):
    def __init__(self, model_name: str, task_names: List[str] = None,
                 batch_size: int = 16, max_length: int = 256):
        self.model_name = model_name
        self.task_names = task_names
        self.batch_size = batch_size
        self.max_length = max_length
        self.progress = 0.0  
        self.uuid = str(uuid.uuid4())

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
    
    def get_uuid(self):
        return self.uuid

