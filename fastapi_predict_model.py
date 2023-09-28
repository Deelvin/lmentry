import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
import threading
from typing import List

import uvicorn
import os

from db_storage import FirestoreClient
from runners.octoairunner import OctoAIRunner

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

# Update the db_storage variable
db_storage = FirestoreClient(os.getenv("FIREBASE_DB_FILE"))



class PredictionRequest(BaseModel):
    model_name: str = "llama-2-70b-chat"
    task_names: List[str] = ["bigger_number","first_alphabetically","first_letter","most_associated_word","smaller_number"]
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
            batch_size = request_data.batch_size
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
    
    #runner.generate_predictions()
    runner.uuid = "36c857bd-02fb-44de-b5c8-70e66513d756"
    #runner.score_predictions()   
    #runner.evaluate_predictions()
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
