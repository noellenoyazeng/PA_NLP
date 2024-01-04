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
