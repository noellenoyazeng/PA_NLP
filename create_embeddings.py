import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel
import pandas as pd
import numpy as np
from tenacity import retry, stop_after_attempt, wait_random_exponential
from typing import Tuple, List
import time

# Call the GCP models
generation_model = TextGenerationModel.from_pretrained("text-bison@002")
embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@002")


# This decorator is used to handle exceptions and apply exponential backoff in case of ResourceExhausted errors.
# It means the function will be retried with increasing time intervals in case of this specific exception.
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def text_generation_model_with_backoff(**kwargs):
    return generation_model.predict(**kwargs).text


def get_embedding(text):
    get_embedding.counter += 1
    try:
        if get_embedding.counter % 100 == 0:
            time.sleep(3)
        return embedding_model.get_embeddings([text])[0].values #Send request to embedding model
    except:
        print('waiting for 60 secs')
        time.sleep(60)
        return embedding_model.get_embeddings([text])[0].values #Send request to embedding model
    
def get_context_from_question(
    question: str, vector_store: pd.DataFrame, sort_index_value: int = 3
) -> Tuple[str, pd.DataFrame]:
    query_vector = np.array(get_embedding(question))
    vector_store["dot_product"] = vector_store["embedding"].apply(
        lambda row: np.dot(row, query_vector)
    )
    # Similarity matching by dot product 
    top_matched = vector_store.sort_values(by="dot_product", ascending=False)[
        :sort_index_value
    ].index
    
    top_matched_df = vector_store.loc[top_matched, ["paragraph_number", "text"]]
    context = "\n".join(top_matched_df["text"].values)
    
    return context, top_matched_df
