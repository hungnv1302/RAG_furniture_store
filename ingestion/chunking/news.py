import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from core.load_settings import load_settings
from ingestion.helper.make_metadata import make_metadata
from ingestion.helper.split_paragraphs import split_paragraph

def html_to_text(html: str) -> str:
  soup = BeautifulSoup(html, "html.parser")
  return soup.get_text(separator=' ', strip = True)

settings = load_settings()
logger = logging.getLogger('ingestion')

def chunk_news():
  file_path = Path(settings['data']['processed_dir'])/'news.json'

  if not file_path.exists():
    logger.error('File not found: {file_path}')
    return []
  
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      news_data = json.load(file)
      logger.info(f'Successfully loaded {len(news_data)} records from {file_path}')

  except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format {e}")
    return []

  except Exception as e:
    logger.error(f'Error reading file {file_path}: {e}')
    return []
  
  if isinstance(news_data, dict):
    news_data = [news_data]

  if not isinstance(news_data, list):
    logger.error('News data is not a list')
    return []
  
  if not news_data:
    logger.warning('No news data found in the data')
    return []
  
  chunks = []
  
  for idx, news_item in enumerate(news_data):
    if not isinstance(news_item, dict):
      logger.warning(f'Skipping invalid news item at index {idx}')
      continue
    
    news_id = news_item.get('id', '')
    news_title = news_item.get('title', '')
    news_excerpt = news_item.get('excerpt', '')
    news_content = news_item.get('content', '')
    news_content_text = html_to_text(news_content)
    news_content_spilt = split_paragraph(news_content_text)
    news_image = news_item.get('thumbnailUrl')
    news_category = news_item.get('category', {})

    base_metadata = {
      "type": "news",
      "source": "news.json",
      "news_id": news_id,
      "news_title": news_title,
      "created_at": datetime.now(timezone.utc).isoformat(),
      "language": "vi"
    }

    CHUNK_PRIORITY = {
      'overview': 1,
      'content': 2,
      'category': 3
    }

    if news_title and news_excerpt:
      text = [
        f'Tên tin tức: {news_title}',
        f'Mô tả ngắn tin tức: {news_excerpt}'
      ]
      if news_image:
        text.append(f'Hình ảnh đại diện: {news_image}')
      chunks.append({
        "text": '\n'.join(text),
        "metadata": make_metadata(base_metadata, chunk_type = 'overview', priority = CHUNK_PRIORITY['overview'])
      })

    for idx, paragraph in enumerate(news_content_spilt):
      if paragraph.strip():
        chunks.append({
          'text': paragraph.strip(),
          'metadata': make_metadata(base_metadata, chunk_type = 'content', priority = CHUNK_PRIORITY['content'], paragraph_index = idx)
        })
    
    if news_category:
      category_name = news_category.get('name', '')
      chunks.append({
        'text': f'Chuyên mục tin tức: {category_name}',
        'metadata': make_metadata(base_metadata, chunk_type = 'category', priority = CHUNK_PRIORITY['category'])
      })

  return chunks



      
