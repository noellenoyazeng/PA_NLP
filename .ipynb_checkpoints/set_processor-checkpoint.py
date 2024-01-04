#Once the project is created in the console, extract the parameters here
PROJECT_ID = !gcloud config get project
PROJECT_ID = PROJECT_ID.n
LOCATION = "europe-west2"
LOCATION_DEPLOY = "europe-west2" #Location to deploy GCP resources

#!gcloud services enable documentai.googleapis.com storage.googleapis.com aiplatform.googleapis.com
