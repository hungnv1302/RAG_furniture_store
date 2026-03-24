import json 
import logging
from pathlib import Path
from datetime import datetime, timezone

from core.load_settings import load_settings
from ingestion.helper import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_project_categories():
  file_path = Path(settings["data"]["processed_dir"])/"projectCategories.json"

  if not file_path.exists():
    logger.error(f'File not found: {file_path}')
    return []

  try:
    with open(file_path, "r", encoding = "utf-8") as file:
      project_categories = json.load(file)
      logger.info(f'Successfully loaded {len(project_categories)} records from {file_path}')

  except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format {e}")
    return []

  except Exception as e:
    logger.error(f'Error reading file {file_path}: {e}')
    return []
  
  if isinstance(project_categories, dict):
    project_categories = [project_categories]

  if not isinstance(project_categories, list):
    logger.error("Project categories data is not a list")
    return []
  
  if not project_categories:
    logger.warning("No project category found in the data")
    return []
  
  chunks = []

  for idx, project_category in enumerate(project_categories):
    if not isinstance(project_category, dict):
      logger.warning(f'Skipping invalid project category at index {idx}')
      continue

    category_id = project_category.get("id")
    category_name = project_category.get("name", "")
    category_slug = project_category.get("slug")

    if not category_name:
      logger.warning(f'Skipping project category with invalid name at {idx}')
      continue

    text_parts = [
      f'Tên loại dự án: {category_name}',
      f'Loại dự án này được dùng để phân loại các dự án liên quan đến {category_name}'
    ]
    
    chunks.append({
      "text": "\n".join(text_parts),
      "metadata": make_metadata({
        "type": "project_category",
        "source": "projectCategories.json",
        "category_id": category_id,
        "category_name": category_name,
        "category_slug": category_slug,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "language": 'vi'
      })
    })

  return chunks

