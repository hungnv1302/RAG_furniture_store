import logging
from qdrant_client import QdrantClient

from core.load_settings import load_settings
from vectorstore.qdrant import get_qdrant_client, ensure_collection
from vectorstore.index import build_qdrant_points

settings = load_settings()
logger = logging.getLogger('vector_database')

QDRANT_CONFIG = settings['vector_database']
COLLECTION_NAME = QDRANT_CONFIG.get('collection_name')

def upsert_chunks(chunks: list[dict]):
  if not chunks:
    logger.warning('No chunks provided to build Qdrant points')
    return []
  
  client: QdrantClient = get_qdrant_client()
  ensure_collection(client)
  points = build_qdrant_points(chunks)

  if not points:
    logger.warning('No points were build from the provided chunks')
    return []
  
  client.upsert(collection_name = COLLECTION_NAME, points = points)
  logger.info(f'Upserted {len(points)} points into collection {COLLECTION_NAME}')