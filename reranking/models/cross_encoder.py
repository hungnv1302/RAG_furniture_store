import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger('reranking')

class CrossEncoderModel:
  def __init__(self, model_name: str, device: str = 'cpu'):
    self.model = CrossEncoder(model_name, device = device)
    logger.info(f'Intialized CrossEncoderModel with model {model_name} on device {device}')

  def rerank(self, pairs: list[tuple[str, str]]) -> list[float]:
    return self.model.predict(pairs).tolist()