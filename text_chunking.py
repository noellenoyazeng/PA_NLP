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


#split into sentences
def text_to_sentences(text):
    sentences = text.split('\n')
    return sentences

def create_sentence_chunks(sentences, chunk_size):
    return [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]
    
def text_to_paragraph(text, chunk_size):
    return create_sentence_chunks(text_to_sentences(text), chunk_size)

def paragraphs_to_df(paragraphs):
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
