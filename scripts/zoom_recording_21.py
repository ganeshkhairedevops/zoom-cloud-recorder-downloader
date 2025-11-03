import os
import requests
import openpyxl
from tqdm import tqdm
from datetime import datetime, timedelta

# ================= CONFIG =================
ACCOUNT_ID = "SAMPLE_ACCOUNT_ID"
CLIENT_ID = "SAMPLE_CLIENT_ID"
CLIENT_SECRET = "SAMPLE_CLIENT_SECRET"
USER_EMAIL = "user@example.com"  # Replace with target user email

# Change these dates per year ↓↓↓
START_DATE = "YYYY-MM-DD"
END_DATE   = "YYYY-MM-DD"
# ==========================================

DOWNLOAD_DIR = "/home/user/zoom_recordings_one_user"
EXCEL_PATH = os.path.join(DOWNLOAD_DIR, "recordings_report.xlsx")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === Helper: Get Access Token ===
def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    res = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET))
    res.raise_for_status()
    return res.json()["access_token"]

# === Helper: Get monthly ranges (Zoom limit) ===
def month_ranges(start, end):
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    while current <= end_date:
        next_month = (current + timedelta(days=32)).replace(day=1)
        yield current.strftime("%Y-%m-%d"), min(next_month - timedelta(days=1), end_date).strftime("%Y-%m-%d")
        current = next_month

# === Helper: Get recordings ===
def get_recordings(token, start, end):
    all_meetings = []
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.zoom.us/v2/users/{USER_EMAIL}/recordings"
    params = {"from": start, "to": end, "page_size": 300}
    while True:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            print("⚠️ Error fetching:", r.text)
            break
        data = r.json()
        all_meetings.extend(data.get("meetings", []))
        if data.get("next_page_token"):
            params["next_page_token"] = data["next_page_token"]
        else:
            break
    return all_meetings

# === Helper: Download file ===
def download_file(url, path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(path, "wb") as f, tqdm(
            desc=os.path.basename(path),
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    size = f.write(chunk)
                    bar.update(size)
    return os.path.getsize(path) / (1024 * 1024)  # size in MB

# === Excel setup (append if exists) ===
def setup_excel():
    if os.path.exists(EXCEL_PATH):
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Recordings"
        ws.append(["File Name", "Recording Date", "Local Path", "Size (MB)"])
    return wb, ws

# === MAIN ===
def main():
    token = get_access_token()
    print("✅ Zoom API Token retrieved.")

    wb, ws = setup_excel()
    total_count = 0

    for start, end in month_ranges(START_DATE, END_DATE):
        print(f"\n📅 Fetching recordings from {start} → {end}")
        meetings = get_recordings(token, start, end)
        total_count += len(meetings)
        print(f"  Found {len(meetings)} meetings this period.")

        for m in meetings:
            meeting_date = m.get("start_time", "")[:10]
            topic = m.get("topic", "Meeting").replace("/", "_")
            for f in m.get("recording_files", []):
                if not f.get("download_url"):
                    continue
                file_name = f"{topic}_{f.get('id')}.mp4"
                local_path = os.path.join(DOWNLOAD_DIR, file_name)
                if os.path.exists(local_path):
                    print(f"⚙️ Skipping existing file: {file_name}")
                    continue
                full_url = f"{f['download_url']}?access_token={token}"
                try:
                    print(f"⬇️  Downloading {file_name}")
                    size = download_file(full_url, local_path)
                    ws.append([file_name, meeting_date, local_path, round(size, 2)])
                except Exception as e:
                    print(f"❌ Failed {file_name}: {e}")

    wb.save(EXCEL_PATH)
    print(f"\n✅ Completed year {START_DATE[:4]}. Added {total_count} meetings.")
    print(f"📁 Excel updated at: {EXCEL_PATH}")

if __name__ == "__main__":
    main()
