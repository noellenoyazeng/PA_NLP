from __future__ import annotations
import sys

if "google.colab" in sys.modules:
    # Automatically restart kernel after installs so that your environment can access the new packages
    import IPython

    app = IPython.Application.instance()
    app.kernel.do_shutdown(True)
else:
    # Otherwise, attempt to discover local credentials as described on https://cloud.google.com/docs/authentication/application-default-credentials
    pass

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

from set_processor import process_document

def split_and_save_pdf(input_pdf_path: str, max_pages_per_file: int):
    # Create a folder to store the split PDFs
    output_folder = os.path.join(os.path.dirname(input_pdf_path), 'pdf_chunks')
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_paths = []
    
    # Open the input PDF
    with open(input_pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        # Calculate the number of files needed
        num_files = (num_pages + max_pages_per_file - 1) // max_pages_per_file
        
        # Split the PDF into multiple files
        for i in range(num_files):
            start_page = i * max_pages_per_file
            end_page = min((i + 1) * max_pages_per_file, num_pages)
            
            pdf_writer = PdfWriter()
            # Etract pages and add to tthe new PDF writer
            for page_num in range(start_page,end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            
            output_pdf_path = os.path.join(output_folder,f'pdf{i+1}.pdf')
            
            # Save the new PDF file
            with open(output_pdf_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
                
            print(f'Saved:{output_pdf_path}')
            pdf_paths.append(output_pdf_path)
            
    return pdf_paths
                
def text_extraction_from_pdf(input_pdf_path):
    max_pages_per_file = 15 # Set the desired maximum number of pages per file
    processor_name = processor.name # Assign the created processor name


    # 1. Split the PDF into pdf chunks of 15 pages max and save their paths 
    pdf_paths = split_and_save_pdf(input_pdf_path, max_pages_per_file)


    # 2. Iterate through the pdf chunks and extract and join their text
    texts = []
    for pdf_path in pdf_paths:
        try: 
            document = process_document(processor_name, file_path=pdf_path)
            texts.append(document.text)
        except Exception as e:
            print("API Resouces temporarily exhausted. Waiting for 60 secs")
            time.sleep(60)
    
    return ''.join(texts) # returns full extracted text, joined form each pdf chunks 
    

                
