import json 
import logging
from pathlib import Path
from datetime import datetime, timezone

from core.load_settings import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_architecture_types():
  file_path = Path(settings["data"]["processed_dir"])/"architectureTypes.json"

  if not file_path.exists():
    logger.error(f'File not found: {file_path}')
    return []

  try:
    with open(file_path, "r", encoding = "utf-8") as file:
      architecture_types = json.load(file)
      logger.info(f'Loaded {len(architecture_types)} projects from {file_path}')

  except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format {e}")
    return []

  except Exception as e:
    logger.error(f'Error reading file {file_path}: {e}')
    return []
  
  if isinstance(architecture_types, dict):
    architecture_types = [architecture_types]

  if not isinstance(architecture_types, list):
    logger.error("Architecture types data is not a list")
    return []
  
  if not architecture_types:
    logger.warning("No architecture types found in the data")
    return []
  
  chunks = []

  for idx, architecture_type in enumerate(architecture_types):
    if not isinstance(architecture_type, dict):
      logger.warning(f'Skipping invalid architecture type at index {idx}')
      continue

    architecture_id = architecture_type.get("id")
    architecture_name = architecture_type.get("name", "")
    architecture_slug = architecture_type.get("slug")
    architecture_image = architecture_type.get("imageUrl", "")

    if not architecture_name:
      logger.warning(f'Skipping architecture type with invalid name at {idx}')
      continue
    if not architecture_image:
      logger.warning(f'Skipping architecture type with invalid image URL at {idx}')
      continue

    base_metadata = {
      "type": "architecture_type",
      "source": "architectureTypes.json",
      "architecture_id": architecture_id,
      "architecture_name": architecture_name,
      "architecture_slug": architecture_slug,
      "created_at": datetime.now(timezone.utc).isoformat(),
      "language": "vi"
    }

    text_parts = [
      f'Loại kiến trúc: {architecture_name}',
      f'Hình ảnh minh họa kiến trúc {architecture_name}: {architecture_image}'
    ]
    
    chunks.append({
      "text": "\n".join(text_parts),
      "metadata": make_metadata(
        base_metadata,
        chunk_type = 'definition',
        priority = 3
      )
    })

  if not chunks:
    logger.warning("No valid architecture type chunks were created")
  return chunks