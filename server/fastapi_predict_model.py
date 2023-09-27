import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from runners.db_storage import FirestoreClient
from pydantic import BaseModel
import threading
from typing import List
from lmentry.predict import generate_all_hf_predictions
from lmentry.tasks.lmentry_tasks import all_tasks
from lmentry.constants import DEFAULT_MAX_LENGTH
from runners.octoairunner import OctoAIRunner
import uvicorn
import os

from dotenv import load_dotenv
    
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins if needed
    allow_methods=["*"],  # Adjust this to restrict HTTP methods if needed
    allow_headers=["*"],  # Adjust this to restrict headers if needed
)

runner = None

# Load environment variables from .env file
load_dotenv()

# Access the FIREBASE_DB_FILE environment variable
firebase_db_file_relative = os.getenv("FIREBASE_DB_FILE")

# Get the current working directory where the script is started
current_directory = os.getcwd()

# Join the relative path with the current directory
firebase_db_file_absolute = os.path.join(current_directory, firebase_db_file_relative)

# Update the db_storage variable
db_storage = FirestoreClient(firebase_db_file_absolute)


class PredictionRequest(BaseModel):
    model_name: str = "llama2-chat-70B-int4"
    task_names: List[str] = ["bigger_number","first_alphabetically","first_letter","most_associated_word","smaller_number"]
    device: str = "cuda"
    batch_size: int = 16
    max_length: int = 70
    runner: str = "octoai"

@app.post("/predict")
async def predict_tasks(request_data: PredictionRequest):
    global runner  # Use the global runner variable

    if request_data.runner == "octoai":
        
        task_names = [task.strip() for task in request_data.task_names[0].split(',')]
        
        
        runner = OctoAIRunner(
            task_names = task_names,
            model_name = request_data.model_name,
            max_length = request_data.max_length,
            batch_size = request_data.batch_size,
            device = request_data.device
        )

        # Start prediction generation in a separate thread
        thread = threading.Thread(target=generate_predictions_async, args=(runner,))
        thread.start()
    else:
        return {"message": f"Incorrect runner {request_data.runner_type}"}

    return {"message": f"Prediction of tasks for {request_data.model_name} model started."}

import time

def generate_predictions_async(runner):
    start_time = time.time()  
    
    runner.generate_predictions()
    runner.score_predictions()   
    runner.evaluate_predictions()
    db_storage.serialize_experiment(runner)

    end_time = time.time()
    execution_time = end_time - start_time
    # Print the execution time
    print(f'Time taken for runner.score_predictions(): {execution_time} seconds')


    return True


@app.get("/progress")
async def get_progress():
    if runner and isinstance(runner, OctoAIRunner):
        progress = runner.get_generation_progress()
        return {"progress": progress}
    else:
        return {"message": "Runner is not an instance of OctoAIRunner"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
