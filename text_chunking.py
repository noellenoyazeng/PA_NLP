from __future__ import annotations

import sys
import pandas as pd


if "google.colab" in sys.modules:
    # Automatically restart kernel after installs so that your environment can access the new packages
    import IPython

    app = IPython.Application.instance()
    app.kernel.do_shutdown(True)
else:
    # Otherwise, attempt to discover local credentials as described on https://cloud.google.com/docs/authentication/application-default-credentials
    pass


#functions
def text_to_sentences(text: str) -> list:
    """
    function to split a text into sentences splitting on lines
    :param text: input text to split
    :return sentences: resulting sentences
    """
    return text.split('\n')

def create_sentence_chunks(
    sentences: str,
    chunk_size: int
) -> list:
    """
    function to create text chuncks from a list of sentences based on a given chunk size.
    :param sentences: list of sentences to create chunks from
    :param chunk_size: given chunk size - number of element, here sentences, per chunk
    :return list: list of chunks of sentences
    """
    return [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]
    
def text_to_paragraph(
    text: str,
    chunk_size: int
) -> list:
    """
    function to create paragraphs from a given text and a given size chunk
    :param text: input text
    :param chunk_size: given chunk size - number of element, here sentences, per chunk
    :return list: list of chunks of text    
    """
    return create_sentence_chunks(text_to_sentences(text), chunk_size)

def paragraphs_to_df(paragraphs: list) -> pd.DataFrame:
    """
    function to transform paragraphs list into a enumerated DataFrame
    :param paragraphs: input the list of paragraphs
    :return dataframe: DataFrame of the paragraphs including each paragraph number
    """
    data = []

    # Iterate through sentence chunks
    for idx, chunk in enumerate(paragraphs, start=1):
        # Merge sentences within the chunk into one string
        merged_text = ''.join(chunk)
        # Append data to the list
        data.append({
            'paragraph_number':idx,
            'text':merged_text
        })
    # DataFrame with different paragraphs
    return pd.DataFrame(data)
