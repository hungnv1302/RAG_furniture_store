from core.schema import RetrievedDocument

class BaseReranker:
  def rerank(self, query: str, documents: list[RetrievedDocument], top_k: int | None = None) -> list[RetrievedDocument]:
    raise NotImplementedError('Rerank method must be implemented by subclasses')
  
