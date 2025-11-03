\
#!/usr/bin/env python3
# zoom_recordings_year.py - year range downloader
import os
import sys
import requests
import openpyxl
from tqdm import tqdm
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)

from scripts.common import get_access_token, DOWNLOAD_DIR, save_row_to_excel, EXCEL_PATH, ensure_excel, USER_EMAIL

START_DATE = "2022-01-01"
END_DATE = "2022-12-31"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
ensure_excel()

def month_ranges(start, end):
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    while current <= end_date:
        next_month = (current + timedelta(days=32)).replace(day=1)
        yield current.strftime("%Y-%m-%d"), min((next_month - timedelta(days=1)), end_date).strftime("%Y-%m-%d")
        current = next_month

def get_recordings(token, start, end):
    meetings = []
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.zoom.us/v2/users/{USER_EMAIL}/recordings"
    params = {"from": start, "to": end, "page_size": 300}
    while True:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            print('Error fetching:', r.status_code, r.text)
            break
        data = r.json()
        meetings.extend(data.get('meetings', []))
        if data.get('next_page_token'):
            params['next_page_token'] = data.get('next_page_token')
        else:
            break
    return meetings

def download_file(url, path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0) or 0)
        with open(path, 'wb') as f, tqdm(total=total, unit='iB', unit_scale=True, unit_divisor=1024, desc=os.path.basename(path)) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
    return os.path.getsize(path) / (1024*1024)

def main():
    token = get_access_token()
    print('Token acquired.')
    count = 0
    for s, e in month_ranges(START_DATE, END_DATE):
        print(f'Fetching from {s} to {e}...')
        meetings = get_recordings(token, s, e)
        print(f'  Found {len(meetings)} meetings.')
        for m in meetings:
            meeting_date = m.get('start_time', '')[:10]
            topic = (m.get('topic') or 'Meeting').replace('/', '_')
            for f in m.get('recording_files', []):
                url = f.get('download_url')
                if not url:
                    continue
                fname = f"{topic}_{f.get('id')}.mp4"
                local_path = os.path.join(DOWNLOAD_DIR, fname)
                if os.path.exists(local_path):
                    print(f'Skipping existing: {fname}')
                    continue
                full_url = f"{url}?access_token={token}"
                try:
                    print(f'Downloading {fname}...')
                    size_mb = download_file(full_url, local_path)
                    save_row_to_excel([fname, meeting_date, local_path, round(size_mb,2)])
                    count += 1
                except Exception as ex:
                    print('Failed', fname, ex)
    print('Done. Total downloaded:', count)
    print('Excel at:', EXCEL_PATH)

if __name__ == '__main__':
    main()
