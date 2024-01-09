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

from config import (folder_pdf_chunks,
                    processor_max_pages,
                    API_waiting_message
)

def split_and_save_pdf(
    input_pdf_path: str,
    max_pages_per_file: int
)-> list:
    """
    The document AI processor has a limit on the number of pages of PDF it can process at one (15). 
    This function split a given PDF of any length into PDFs of a given number - here 15.
    It first calculates the num of files needed to split the initial PDF into PDFs under a maximum number of pages, split the PDF following this number and save them under new paths     in a pdf_paths folder. The files in the new folder follow occuring order in the PDF. Each of those new paths is saved in a list under.
    :param input_pdf_path: initial PDF path
    :param max_pages_per_file: max page processable by processor - 15 for document AI
    :return: list of paths corresponding to PDF chunks in occuring order
    """
    # Create a folder to store the split PDFs
    output_folder = os.path.join(os.path.dirname(input_pdf_path), folder_pdf_chunks)
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
                
def text_extraction_from_pdf(input_pdf_path: str)-> str:
    """
    function to extract text from pdf given pdf path. It uses the defined split_and_save_pdf and process_document functions. 
    The initial PDF is split into PDF of given size following the processor maximum size constrain, the text is extracted by the processor on each of the PDF chunks and a 60 secs wait time is included if computing resources are temporary exhausted.
    The texts are then joined together and returned as a whole text. Order of occurence is preserve
    :param input_pdf_path: path of PDF file
    :return str: whole text extracted from PDF
    
    """
    max_pages_per_file = processor_max_pages # Set the desired maximum number of pages per file
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
            print(API_waiting_message)
            time.sleep(60)
    
    return ''.join(texts) # returns full extracted text, joined form each pdf chunks 
    

                
