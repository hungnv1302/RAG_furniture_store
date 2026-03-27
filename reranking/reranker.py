import logging 

from core.schema import RetrievedDocument
from reranking.base import BaseReranker
from reranking.models.cross_encoder import CrossEncoderModel

logger = logging.getLogger('reranking')

class CrossEncoderReranker(BaseReranker):
  def __init__(self, model: CrossEncoderModel):
    self.model = model

  def rerank(self, query:str, documents: list[RetrievedDocument], top_k: int | None = None) -> list[RetrievedDocument]:
    if not documents:
      logger.info('No documents to rerank')
      return []
    
    pairs = [(query, documents.text) for document in documents]
    
    scores = self.model.rerank(pairs)

    for document, score in zip(documents, scores):
      document.metadata['rerank_score'] = float(score)

    documents.sort(key = lambda d: d.metadata['rerank_score'], reverse=True)

    if top_k is not None:
      documents = documents[:top_k]

    logger.info(f'Reranked {len(documents)} documents')
    return documents