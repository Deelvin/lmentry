from abc import ABC, abstractmethod
from typing import List

OCTOAI_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNkMjMzOTQ5In0.eyJzdWIiOiIwMDE0ODBmMS0yZjUyLTQ0ZjctOTM3Yy1lODQ0OTk2YzllN2UiLCJ0eXBlIjoidXNlckFjY2Vzc1Rva2VuIiwidGVuYW50SWQiOiJlZmZhMTI2Mi1mNzQ2LTRhOTEtOTg0NS04YWUyZWE3ZDQxNTkiLCJ1c2VySWQiOiJiMmE0Y2I0Yi1kNDllLTRiZDYtYjhkMi1lOGI3ZjQwNDIyNjciLCJyb2xlcyI6WyJGRVRDSC1ST0xFUy1CWS1BUEkiXSwicGVybWlzc2lvbnMiOlsiRkVUQ0gtUEVSTUlTU0lPTlMtQlktQVBJIl0sImF1ZCI6IjNkMjMzOTQ5LWEyZmItNGFiMC1iN2VjLTQ2ZjYyNTVjNTEwZSIsImlzcyI6Imh0dHBzOi8vaWRlbnRpdHkub2N0b21sLmFpIiwiaWF0IjoxNjk0NTA4MTY3fQ.M5PAmS70ijpiiUPszh53FYEwO5RDOBr3kIU6BMu__mRrofE0HC8c4k8fGy8MnR-BzECL_fCPNHNHJQSROgCbhEkaXS8JRW0mTMjMcayIM7yU1zrYX46Tznn23bhegjSSYCyCXRED2UzmPICk9euyFcKgwPuHVDqb7qeJGxRAq_SoTCZWn1Dhsxue0l6QmDtL-v3tJuAc0MOZpYWZZVT5JMIDJa3PMSe-lv3KjjbXwgldGRBGiA9I2op9K5DWEgUZy5LZIiZ2soSWQlNVuii0KMCA7vlQkEurChdwyvcorDPVKjzVT6QCpZdgnSyV0DcTgPTuCibd70BWmWupq0if9w"


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

