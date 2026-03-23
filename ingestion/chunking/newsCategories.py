import json 
import logging
from pathlib import Path

from core.load_settings import load_settings

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

    news_category_id = news_category.get("id")
    news_category_name = news_category.get("name", "")
    news_category_slug = news_category.get("slug")
    news_category_description = news_category.get("description")

    if not news_category_name or not isinstance(news_category_name, str):
      logger.warning(f'Skipping news category with invalid name at {idx}')
      continue

    text_parts = [
      f'Loại tin tức: {news_category_name}'
    ]
    
    chunks.append({
      "text": "\n".join(text_parts),
      "metadata":{
        "type": "news_category",
        "source": "newsCategories.json",
        "news_category_id": news_category_id,
        "news_category_name": news_category_name,
        "news_category_slug": news_category_slug,
        "news_category_description": news_category_description
      }
    })

  if not chunks:
    logger.warning("No valid news category chunks were created")
  return chunks

