from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL

_model = SentenceTransformer(EMBEDDING_MODEL)

def embed(texts):

    if isinstance(texts, str):
        texts = [texts]

    return _model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )