# Zoom Cloud Recorder Downloader

**Overview**
This repository contains scripts to download a single user's Zoom cloud recordings year-by-year, store them locally, and maintain a consolidated Excel report `recordings_report.xlsx` in the repository root.

**Structure**
- `scripts/` - year-wise scripts and shared `common.py`
- `zoom_recordings_one_user/` - recordings will be downloaded here
- `recordings_report.xlsx` - Excel master report (created on first run)
- `requirements.txt` - Python dependencies

**Quickstart**
1. Clone or unzip this repo.
2. Edit `scripts/common.py` and replace sample credentials:
   ```py
   ACCOUNT_ID = "YOUR_ACCOUNT_ID"
   CLIENT_ID = "YOUR_CLIENT_ID"
   CLIENT_SECRET = "YOUR_CLIENT_SECRET"
   USER_EMAIL = "target-user@example.com"
   ```
3. (Optional but recommended) Use environment variables instead of editing files directly.
4. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
5. Run year scripts (example):
   ```bash
   python3 scripts/zoom_recordings_2021.py
   python3 scripts/zoom_recordings_2022.py
   ...
   ```

**Notes**
- Scripts skip already-downloaded files.
- Excel file is appended (no overwrite).
- Zoom API limits: month-by-month fetching is used to respect Zoom's date-range limits.
- Replace placeholder credentials before running. Never commit real credentials to GitHub.

**License**
MIT
