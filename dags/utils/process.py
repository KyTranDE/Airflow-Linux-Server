from datetime import datetime, timedelta
import re
import json
import os
import logging


def convert_to_date(text):
    current_date = datetime.now()
    
    patterns = {
        r"(\d+) tuần trước": "weeks",
        r"(\d+) ngày trước": "days",
        r"(\d+) giờ trước": "hours",
        r"(\d+) năm trước": "years",
        r"(\d+) tháng trước": "months",
        r"một tuần trước": "1 weeks",
        r"một năm trước": "1 years",
        r"một tháng trước": "1 months",
        r"một ngày trước": "1 days",
        r"một giờ trước": "1 hours"
    }
    
    for pattern, unit in patterns.items():
        match = re.search(pattern, text)
        if match:
            if unit == "weeks":
                weeks = int(match.group(1))
                return current_date - timedelta(weeks=weeks)
            elif unit == "days":
                days = int(match.group(1))
                return current_date - timedelta(days=days)
            elif unit == "hours":
                hours = int(match.group(1))
                return current_date - timedelta(hours=hours)
            elif unit == "years":
                years = int(match.group(1))
                return current_date.replace(year=current_date.year - years)
            elif unit == "months":
                months = int(match.group(1))
                return current_date - timedelta(days=months * 30)
            elif unit == "1 weeks":
                return current_date - timedelta(weeks=1)
            elif unit == "1 years":
                return current_date.replace(year=current_date.year - 1)
            elif unit == "1 months":
                return current_date - timedelta(days=30)
            elif unit == "1 days":
                return current_date - timedelta(days=1)
            elif unit == "1 hours":
                return current_date - timedelta(hours=1)
    return None

def extract_phone_numbers(text):
    phone_pattern = re.compile(r"(?:\d{3,4}[ .]?\d{3}[ .]?\d{3,4})") 
    phone_numbers = phone_pattern.findall(text)
    if phone_numbers:
        return phone_numbers
    return [0]

def extract_reviews(text):
    review_pattern = re.search(r"(\d+)\s+bài đánh giá", text) 
    if review_pattern:
        return int(review_pattern.group(1)) 
    return 0

from datetime import datetime

def append_data_to_json(file_path, data, lock):
    try:
        def convert_to_serializable(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to string
            raise TypeError(f"Type {type(obj)} is not serializable")
        
        with lock:
            if os.path.exists(file_path):
                with open(file_path, 'r+', encoding='utf-8-sig') as infile:
                    try:
                        existing_data = json.load(infile)
                        if not isinstance(existing_data, list):
                            # print(f"Warning: {file_path} không phải là một danh sách. Tạo mới danh sách.")
                            logging.error(f"Warning: {file_path} không phải là một danh sách. Tạo mới danh sách.")
                            existing_data = []
                    except json.JSONDecodeError:
                        logging.error(f"Warning: {file_path} không chứa JSON hợp lệ. Tạo mới danh sách.")
                        existing_data = []
                    existing_data.append(data)
                    infile.seek(0)
                    json.dump(existing_data, infile, ensure_ascii=False, indent=4, default=convert_to_serializable)
            else:
                with open(file_path, 'w', encoding='utf-8-sig') as outfile:
                    json.dump([data], outfile, ensure_ascii=False, indent=4, default=convert_to_serializable)
    except Exception as e:
        logging.error(f'Error appending data to JSON file: {e}')
