import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
import pandas as pd
import numpy as np
from tenacity import retry, stop_after_attempt, wait_random_exponential
from typing import Tuple, List
import time

from config import (text_bison2_ID,
                    gecko2_embedding_ID,
                    top_matched_number,
                    dot_product_col, embedding_col,
                    paragraph_number_col,
                    text_col,
                    API_waiting_message
)


# Call the GCP models
generation_model = TextGenerationModel.from_pretrained(LLM_ID)
embedding_model = TextEmbeddingModel.from_pretrained(embedding_model_ID)


# This decorator is used to handle exceptions and apply exponential backoff in case of ResourceExhausted errors.
# It means the function will be retried with increasing time intervals in case of this specific exception.
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def text_generation_model_with_backoff(**kwargs):
    return generation_model.predict(**kwargs).text


def get_embedding(text: str) -> list:
    """
    function to transform a given text into embeddings, numerical vector, using GCP's gecko 2 embedding model. It includes a 60 secs wait time if API resources are temporarily exhausted. 
    :param text: input text to transform
    :return embeddings: numerical vector corresponding to the embedding of the given text
    """
    get_embedding.counter += 1
    try:
        if get_embedding.counter % 100 == 0:
            time.sleep(3)
        return embedding_model.get_embeddings([text])[0].values #Send request to embedding model
    except:
        print(API_waiting_message)
        time.sleep(60)
        return embedding_model.get_embeddings([text])[0].values #Send request to embedding model
    
def get_context_from_question(
    question: str,
    vector_store: pd.DataFrame,
    sort_index_value: int = top_matched_number
) -> Tuple[str, pd.DataFrame]:
    """
    function to select context to answer a given question. It first creates the embeddings of the given question, then performs a dot product similarity search in the DataFrame of text embeddings to find the most semantically similar paragraphs, which are used as context for the question. The number of paragraphs used for context can be set manually.
    :param question: user's question on document
    :param vector_store: DataFrame of paragraphs embeddings
    :sort_index_value: number of top matched paragraphs used for context. set to 3
    """
    query_vector = np.array(get_embedding(question))
    vector_store[dot_product_col] = vector_store[embedding_col].apply(
        lambda row: np.dot(row, query_vector)
    )
    # Similarity matching by dot product 
    top_matched = vector_store.sort_values(by="dot_product", ascending=False)[
        :sort_index_value
    ].index
    
    top_matched_df = vector_store.loc[top_matched, [paragraph_number_col, text_col]]
    context = "\n".join(top_matched_df[text_col].values)
    
    return context, top_matched_df
