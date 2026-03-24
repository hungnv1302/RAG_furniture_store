import logging
import json
from pathlib import Path
from datetime import datetime, timezone

from core.load_settings import load_settings
from ingestion.helpers.make_metadata import make_metadata

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_company_info():
  file_path = Path(settings['data']['processed_dir'])/"companyInfo.json"

  if not file_path.exists():
    logger.error(f'File not found {file_path}')
    return []
  
  try:
    with open(file_path, "r", encoding="utf-8") as file:
      company_info = json.load(file)
      logger.info(f'Successfully loaded {len(company_info)} companies from {file_path}')
  
  except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format {e}")
    return []

  except Exception as e:
    logger.error(f'Error reading file {file_path}: {e}')
    return []
  
  if isinstance(company_info, dict):  
    company_info = [company_info]

  if not isinstance(company_info, list):
    logger.error("Company info data is not a list")
    return []
  
  if not company_info:
    logger.warning("No company info found in the data")
    return []
  
  chunks = []

  for idx, info in enumerate(company_info):
    if not isinstance(info, dict):
      logger.warning(f'Skipping invalid company info at index {idx}')
      continue

    company_name = info.get("companyName", "")
    company_slogan = info.get("companySlogan", "")
    company_description = info.get("companyDescription", "")
    company_hotlines = info.get("hotlines", [])
    company_emails = info.get("emails", [])
    company_main_address = info.get("mainAddress", "")
    company_working_hours = info.get("workingHours", "")
    company_website = info.get("website", "")

    company_social_links = info.get("socialLinks", {})
    if isinstance(company_social_links, dict):
      company_social_text = ", ".join([f"{key}: {value}" for key, value in company_social_links.items() if value])

    company_total_employees = info.get("totalEmployees")
    company_total_projects = info.get("totalProjects")

    base_metadata = {
      'type': 'company_info',
      'source': 'companyInfo.json',
      'company_name': company_name,
      'created_at': datetime.now(timezone.utc).isoformat(),
      'language': 'vi'
    }

    CHUNK_PRIORITY = {
      'overview': 1,
      'contact_details': 2,
      'social_links': 3,
      'additional_info': 4
    }

    if company_name and company_slogan and company_description:
      chunks.append({
        'text': f'Tên công ty: {company_name}\nKhẩu hiệu: {company_slogan}\nMô tả: {company_description}',
        'metadata': make_metadata(base_metadata, chunk_type='overview', priority=CHUNK_PRIORITY['overview'])
      })

    if company_hotlines or company_emails or company_working_hours or company_main_address:
      text_parts = []
      if company_hotlines:
        text_parts.append(f'Số điện thoại liên hệ: {', '.join(company_hotlines)}')
      if company_emails:
        text_parts.append(f'Email liên hệ: {', '.join(company_emails)}')
      if company_working_hours:
        text_parts.append(f'Giờ làm việc: {company_working_hours}')
      if company_main_address:
        text_parts.append(f'Địa chỉ chính: {company_main_address}')
      chunks.append({
        'text': text_parts,
        'metadata': make_metadata(base_metadata, chunk_type='contact_details', priority=CHUNK_PRIORITY["contact_details"])
      })
    
    if company_social_links or company_website:
      text_parts = []
      if company_website:
        text_parts.append(f'Website: {company_website}')
      if company_social_links:
        text_parts.append(f'Mạng xã hội: {company_social_text}')
      chunks.append({
        'text': text_parts,
        'metadata': make_metadata(base_metadata, chunk_type='social_links', priority=CHUNK_PRIORITY['social_links'])
      })

    if company_total_employees or company_total_projects:
      text_parts = []
      if company_total_employees:
        text_parts.append(f'Tổng số nhân viên: {company_total_employees}')
      if company_total_projects:
        text_parts.append(f'Tổng số dự án: {company_total_projects}')
      chunks.append({
        'text': text_parts,
        'metadata': make_metadata(base_metadata, chunk_type='additional_info', priority=CHUNK_PRIORITY['additional_info'])
      })
    
  return chunks




