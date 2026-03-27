import logging

from core.schema import RetrievedDocument

logger = logging.getLogger('retrieval')

class ContextBuilder:
  def __init__(self, max_documents: int = 5, max_context_length: int = 3000, separator: str = '\n\n---\n\n'):
    self.max_documents = max_documents
    self.max_context_length = max_context_length
    self.separator = separator

  def context_builder(self, documents: list[RetrievedDocument]) -> str:
    if not documents:
      logger.warning('No documents provided to build context')
      return ""

    context_parts = []
    current_length = 0

    for document in documents[:self.max_documents]:
      text = documents.text.strip()
      if not text:
        continue

      if current_length + len(text) > self.max_context_length:
        remaining = self.max_context_length - current_length
        if remaining <= 0:
          break
        text = text[:remaining]

      context_parts.append(text)
      current_length += len(text)

    context = self.separator.join(context_parts)
    logger.info(f'Build context of length {len(context)} using {len(context_parts)} documents')
    return context

