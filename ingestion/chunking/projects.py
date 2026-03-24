import logging
import json
from pathlib import Path
from datetime import datetime, timezone

from core.load_settings import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger('ingestion')

def chunk_projects():
  file_path = Path(settings['data']['processed_dir'])/'projects.json'

  if not file_path.exists():
    logger.error(f'File not found: {file_path}')
    return []
  
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      projects = json.load(file)
      logger.info(f'Loaded {len(projects)} projects from {file_path}')

  except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format {e}")
    return []

  except Exception as e:
    logger.error(f'Error reading file {file_path}: {e}')
    return []
  
  if isinstance(projects, dict):
    projects = [projects]

  if not isinstance(projects, list):
    logger.error(f'Projects data is not a list')
    return []
  
  if not projects:
    logger.warning('No projects found in the file')
    return []
  
  chunks = []

  for idx, project in enumerate(projects):
    if not isinstance(project, dict):
      logger.warning(f'Skipping invalid project at index {idx}')
      continue

    project_id = project.get('id')
    project_title = project.get('title', '')
    project_slug = project.get('slug', '')
    project_description = project.get('description', '')
    project_investor = project.get('investor', '')
    project_location = project.get('location', '')
    project_area = project.get('area', '')
    project_complete_date = project.get('complete_date', '')
    project_interior_style = project.get('interiorStyle', {})
    project_architecture_type = project.get('architectureType', {})
 
    base_metadata = {
      "type": "project",
      "source": "projects.json",
      "project_id": project_id,
      "project_title": project_title,
      "project_slug": project_slug,
      "created_at": datetime.now(timezone.utc).isoformat(),
      "language": "vi"
    }

    CHUNK_PRIORITY = {
      'overview_title': 1,
      'overview_description': 2,
      'overview_architecture_interior': 3,
      'overview_location_investor': 4,
      'overview_specs': 5,
    }

    if project_title:
      chunks.append({
        "text": f'Tiêu đề dự án: {project_title}',
        "metadata": make_metadata(base_metadata, chunk_type="overview_title", priority=CHUNK_PRIORITY['overview_title'])
      })

    if project_description:
      chunks.append({
        "text": f'Mô tả dự án: {project_description}',
        "metadata": make_metadata(base_metadata, chunk_type='overview_description', priority=CHUNK_PRIORITY['overview_description'])
      })

    if project_location or project_investor:
      text_parts = []
      if project_location:
        text_parts.append(f'Vị trí: {project_location}')
      if project_investor:
        text_parts.append(f'Chủ đầu tư: {project_investor}')
      chunks.append({
        "text": ' | '.join(text_parts),
        "metadata": make_metadata(base_metadata, chunk_type='overview_location_investor', priority=CHUNK_PRIORITY['overview_location_investor'])
      })

    if project_area or project_complete_date:
      text_parts = []
      if project_area:
        text_parts.append(f'Diện tích: {project_area}')
      if project_complete_date:
        text_parts.append(f'Ngày hoàn thành: {project_complete_date}')
      chunks.append({
        'text': ' | '.join(text_parts),
        'metadata': make_metadata(base_metadata, chunk_type='overview_specs', priority=CHUNK_PRIORITY['overview_specs'])
      })

    if project_architecture_type or project_interior_style:
      text_parts = []
      if project_architecture_type:
        arch_type_name = project_architecture_type.get('name', '')
        if arch_type_name:
          text_parts.append(f'Loại kiến trúc: {arch_type_name}')
      if project_interior_style:
        interior_style_name = project_interior_style.get('name', '')
        if interior_style_name:
          text_parts.append(f'Phong cách nội thất: {interior_style_name}')
      chunks.append({
        'text': ' | '.join(text_parts),
        'metadata': make_metadata(base_metadata, chunk_type='overview_architecture_interior', priority=CHUNK_PRIORITY['overview_architecture_interior'])
      })
      
  return chunks