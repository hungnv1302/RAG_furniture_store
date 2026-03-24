import json 
import logging
from pathlib import Path
from datetime import datetime, timezone

from core.load_settings import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_news_categories():
  file_path = Path(settings["data"]["processed_dir"])/"newsCategories.json"

  if not file_path.exists():
    logger.error(f'File not found: {file_path}')
    return []

  try:
    with open(file_path, "r", encoding = "utf-8") as file:
      news_categories = json.load(file)
      logger.info(f'Successfully loaded {len(news_categories)} records from {file_path}')

  except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format {e}")
    return []

  except Exception as e:
    logger.error(f'Error reading file {file_path}: {e}')
    return []
  
  if isinstance(news_categories, dict):
    news_categories = [news_categories]

  if not isinstance(news_categories, list):
    logger.error("News categories data is not a list")
    return []
  
  if not news_categories:
    logger.warning("No news category found in the data")
    return []
  
  chunks = []

  for idx, news_category in enumerate(news_categories):
    if not isinstance(news_category, dict):
      logger.warning(f'Skipping invalid news category at index {idx}')
      continue

    category_id = news_category.get("id")
    category_name = news_category.get("name", "")
    category_slug = news_category.get("slug")

    if not category_name:
      logger.warning(f'Skipping news category with missing name at index {idx}')
      continue

    base_metadata = {
      'type': 'news_category',
      'source': 'newsCategories.json',
      'category_id': category_id,
      'category_name': category_name,
      'category_slug': category_slug,
      'created_at': datetime.now(timezone.utc).isoformat(),
      'language': 'vi'
    }

    text_parts = [
      f'Tên danh mục tin tức: {category_name}',
      f'Danh mục này được dùng để phân loại các bài viết liên quan đến {category_name}.'
    ]

    chunks.append({
      'text': '\n'.join(text_parts),
      'metadata': make_metadata (
        base_metadata,
        chunk_type = 'definition',
        priority = 3
      )
    })

  return chunks

