from __future__ import annotations

import sys
import backoff
from tenacity import retry, stop_after_attempt, wait_random_exponential
from google.api_core.exceptions import ResourceExhausted
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import AlreadyExists
from google.cloud import documentai
import numpy as np
import glob
import os
from typing import Dict, List
import pandas as pd
from logging import error
import re
import textwrap
from typing import Tuple, List
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
from PyPDF2 import PdfReader, PdfWriter
import json
import time
import numpy as np
import glob
import subprocess
from config import gcloud, config, get, project, LOCATION, LOCATION_DEPLOY, pdf_mime_type, PROCESSOR_DISPLAY_NAME


if "google.colab" in sys.modules:
    # Automatically restart kernel after installs so that your environment can access the new packages
    import IPython

    app = IPython.Application.instance()
    app.kernel.do_shutdown(True)
else:
    # Otherwise, attempt to discover local credentials as described on https://cloud.google.com/docs/authentication/application-default-credentials
    pass




#Once the project is created in the console, extract the parameters here
#PROJECT_ID = !gcloud config get project

try:
    project_id = subprocess.check_output([gcloud, config, get, project], text = True).strip()
    PROJECT_ID = project_id
    print(f"PROJECT_ID set to: {PROJECT_ID}")
except subprocess.CalledProcessError as e:
    print(f"Error getting project ID: {e}")
    PROJECT_ID = None
    

# See https://cloud.google.com/document-ai/docs/regions for all options.
project_id = PROJECT_ID
location = LOCATION

#!gcloud services enable documentai.googleapis.com storage.googleapis.com aiplatform.googleapis.com

# Must be unique per project, e.g.: "My Processor": is this set automatically?
processor_display_name = PROCESSOR_DISPLAY_NAME

# You must set the `api_endpoint` if you use a location other than "us".
client_options = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")



#1. Create the processor: you can not create multiple processors with the same display name
def create_processor(
    project_id: str,
    location: str,
    processor_display_name: str
) -> documentai.Processor:
    """
    function to create OCR processor, i.e. PDF reader using the GCP document AI API.
    The document processor service is used to first set the correct client parameters. Then the exact location of the project is extracted as path to create the pretrained OCR processor.
    :param project_id: ID of the project
    :param location: chosen location for GCP resources
    :param processor_display_name: display name of the created processor
    :return: pre-trained OCR processor ready for usage by calling display name
    """
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)
    parent = client.common_location_path(project_id, location)
    
    return client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            display_name=processor_display_name, type_="OCR_PROCESSOR"
        ),
    )


try:
    processor = create_processor(project_id, location, processor_display_name)
    print(f"Created Processor {processor.name}")
except AlreadyExists as e:
    print(
        f"Processor already exits, change the processor name and rerun this code. {e.message}"
    )

    

#2. Define process document function which takes the processor name and file path of the document and extracts the text from the document.  
def process_document(
    processor_name: str,
    file_path: str,
) -> documentai.Document:
    """
    function which takes the processor name and file path of the document and extracts the text from the document. 
    It first read the given file into memory, load the binary datat into a document AI rawdocument object, configure the process request and finally process the given file using the given processor.
    :param processor_name: name of pre-trained OCR processor
    :param file_path: path the the PDF document
    :return: document object 
    """
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(
        content=image_content, mime_type=pdf_mime_type
    )

    # Configure the process request
    request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)

    result = client.process_document(request=request)

    return result.document

