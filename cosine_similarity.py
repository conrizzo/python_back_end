# stat

from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")


def compute_similarity(sentence1, sentence2):
    model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

    # Compute embeddings
    embedding1 = model.encode(sentence1, convert_to_tensor=True)
    embedding2 = model.encode(sentence2, convert_to_tensor=True)

    # Compute cosine similarity
    cosine_score = util.cos_sim(embedding1, embedding2)

    # Return a dictionary
    result = {
        "sentence1": sentence1,
        "sentence2": sentence2,
        "similarity_score": cosine_score.item()
    }
    return result



"""
print(compute_similarity("I like to eat apples", "I like to eat oranges"))

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

from nltk.tokenize import word_tokenize

tokens = word_tokenize("I like to eat apples")
tagged_words = nltk.pos_tag(tokens)

print(tokens)
print(tagged_words)
"""