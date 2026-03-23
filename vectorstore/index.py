import logging
import uuid

from core.load_settings import load_settings
from embedding.embed_texts import embed_texts


settings = load_settings()
logger = logging.getLogger('vector_database')

def build_qdrant_points(chunks: list[dict]) -> list[dict]:
  if not chunks:
    logger.warning('No chunks provided to build Qdrant points')
    return []
  
  texts = [chunk['text'] for chunk in chunks]
  if not texts:
    logger.warning('No text found in the provided chunks')
    return []
  
  embeddings = embed_texts(texts)
  if not embeddings:
    logger.warning('No embeddings generated for the provided texts')
    return []
  
  points = []

  for chunk, vector in zip(chunks, embeddings):
    points.append({
      'id': str(uuid.uuid4()),
      'vector': vector,
      'payload':{
        'text': chunk['text'],
        **chunk.get('metadata', {})
      }
    })

  logger.info(f'Built {len(points)} Qdrant points')
  return points