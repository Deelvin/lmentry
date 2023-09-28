from cProfile import run
import os
import firebase_admin
from firebase_admin import credentials, firestore, storage 


from runners.baserunner import BaseRunner

import csv
import json
from datetime import datetime

class FirestoreClient:
    def __init__(self, json_filename):
        self.json_filename = json_filename
        self.db = None
        self.initialize_db()

    def initialize_db(self):
        if not self.json_filename:
            raise ValueError("Firebase JSON filename not provided.")

        # Get the directory containing the script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the JSON file
        json_file_path = os.path.join(script_directory, self.json_filename)

        # Initialize Firebase Admin SDK with the provided service account key JSON
        cred = credentials.Certificate(json_file_path)
        firebase_admin.initialize_app(cred)

        # Initialize Firestore client
        self.db = firestore.client()
        
        
    import csv
    import json

    def parse_csv_and_calculate_average(self, uuid):
        # Initialize variables to store data and calculate average
        data = {}
        total_values = 0
        total_sum = 0.0

        # Get the directory containing the script
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Navigate up one level to the parent directory
        parent_directory = os.path.dirname(script_directory)

        # Construct the full path to the JSON file by concatenating with the "results" folder
        csv_file_path = os.path.join(parent_directory, f"results/accuracy_per_task_{uuid}.csv")

        # Read the CSV file and parse its contents
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            for row in csv_reader:
                key, value = row[0], float(row[1])
                data[key] = value
                total_sum += value
                total_values += 1

        # Calculate the average value
        average = total_sum / total_values if total_values > 0 else 0.0

        # Create a JSON object
        result = {
            **data,  # Include the key-value pairs from the CSV
            "average": average  # Add the average value
        }

        return result
        
    def serialize_experiment_artefacts(self, runner: BaseRunner):
        if not self.db:
            raise ValueError("Firestore database not initialized.")


    def upload_tasks_to_firestore(self, tasks, root_directory, project_id, service_account_key_path):
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_key_path)
        firebase_admin.initialize_app(cred, {"storageBucket": f"{project_id}.appspot.com"})


        # Reference to the Firestore collection
        experiments_ref = self.db.collection("experiments")

        # Dictionary to store all log file URLs
        log_file_urls = {}

        # Iterate over the list of tasks (folders)
        for task_name in tasks:
            task_directory = os.path.join(root_directory, task_name)
            if os.path.isdir(task_directory):
                task_data = {}

                for log_file in os.listdir(task_directory):
                    if log_file.endswith(".json"):
                        model_name = log_file.split('.')[0]
                        log_file_path = os.path.join(task_directory, log_file)

                        # Upload the log file to Firebase Cloud Storage
                        bucket = storage.bucket()
                        blob = bucket.blob(f"{task_name}/{model_name}.json")
                        blob.upload_from_filename(log_file_path)

                        # Get the URL to the uploaded file
                        file_url = blob.public_url

                        # Store the log file URL
                        log_file_urls[model_name] = file_url

                        # Add log file data to task_data
                        task_data[model_name] = {"log_data_url": file_url}

                # Define the experiment data for the task
                experiment_data = {
                    "task_name": task_name,
                    "logs": task_data,
                    # Add other experiment data as needed
                }

                # Add the experiment record to Firestore
                experiments_ref.add(experiment_data)


    def serialize_experiment(self, runner: BaseRunner):
        """
        Serialize an experiment using a BaseRunner object and save it in Firestore.

        Args:
            runner (BaseRunner): An instance of the BaseRunner class.
        """
        if not self.db:
            raise ValueError("Firestore database not initialized.")

        results_data = self.parse_csv_and_calculate_average(runner.get_uuid())

        # Define the Firestore collection name where you want to store the experiment data
        collection_name = "experiments"

        # Create a new document reference within the specified collection
        new_experiment_ref = self.db.collection(collection_name).document()


        experiment_data = {
            "data": results_data,
            "model_name": runner.model_name,
            "timestamp": datetime.now().isoformat(),
            "batch_size": runner.batch_size,
            "performance": runner.tasks_per_second,
            "backend": "octoai.cloud",
            "max_length": runner.max_length,
        }

        # Set the data in the Firestore document
        new_experiment_ref.set(experiment_data)

        # Optionally, you can return the ID of the newly created Firestore document
        return new_experiment_ref.id


    