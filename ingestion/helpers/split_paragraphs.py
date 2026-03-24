import logging

logger = logging.getLogger('ingestion')

def split_paragraph(text: str, max_len = 400):
  if not text:
    logger.warning("Empty text provided to split paragraph")
    return []
  
  sentences = text.split('. ')
  out = []
  buf = ''

  for sentence in sentences:
    sentence = sentence.strip()
    if not sentence:
      logger.warning('Empty sentence after stripping')
      continue 

    while len(sentence) > max_len:
      cut = sentence.rfind('. ', 0, max_len)
      if cut == -1:
        cut = max_len
      
      chunk = sentence[:cut].strip()
      if not chunk:
        out.append(chunk)
      sentence = sentence[cut:].strip()
    
    if len(buf) + len(sentence) + 2 <= max_len:
      buf += sentence + '.'
    else:
      out.append(buf.strip())
      buf = sentence + '.'

  if buf:
    out.append(buf.strip())
    
  return out