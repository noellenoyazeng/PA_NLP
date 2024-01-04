#split into sentences
def text_to_sentences(text):
    sentences = text.split('\n')
    return sentences

def create_sentence_chunks(sentences, chunk_size):
    sentence_chunks = [sentences[i:i+chunk_size] for i in range(0, len(sentences), chunk_size)]
    return sentence_chunks

def text_to_paragraph(text, chunk_size):
    return create_sentence_chunks(text_to_sentences(text), chunk_size)

def paragraphs_to_df(paragraphs):
    data = []

    # Iterate through sentence chunks
    for idx, chunk in enumerate(sentence_chunks, start=1):
        # Merge sentences within the chunk into one string
        merged_text = ''.join(chunk)
        # Append data to the list
        data.append({
            'paragraph_number':idx,
            'text':merged_text
        })
    # DataFrame with different paragraphs
    return pd.DataFrame(data)
    
# chunk_size = 40
# sentence_chunks = text_to_paragraph(text, chunk_size)
# df = paragraphs_to_df(sentence_chunks)
