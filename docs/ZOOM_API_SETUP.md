# How to Create Zoom API Credentials

This guide explains how to create **Server-to-Server OAuth credentials** in Zoom Marketplace to use with this project.

---

## ✅ Step 1 — Sign in to Zoom Marketplace
1. Open: https://marketplace.zoom.us/
2. Sign in using your Zoom account.

---

## ✅ Step 2 — Create a New App
1. Click **Develop** ➝ **Build App**
2. Select **Server-to-Server OAuth**
3. Click **Create**

---

## ✅ Step 3 — Basic App Info
Fill in required details:
- App Name (e.g., `Cloud Recorder Downloader`)
- Company name
- Developer contact email

Then click **Continue**.

---

## ✅ Step 4 — Add Required Scopes
Go to the **Scopes** tab → Click **Add Scopes**

Add the following permissions:

| Category | Scope Name | Required |
|---------|------------|:-------:|
| Cloud Recording | `recording:read:admin` | ✅ |
| Cloud Recording | `recording:read:list_records` | ✅ |
| User Information | `user:read:admin` | ✅ |

Click **Done** → **Continue**

---

## ✅ Step 5 — App Activation
1. Go to **Activation**
2. Turn ON the app to make it **Active**

---

## ✅ Step 6 — Get API Credentials
Go to the **App Credentials** tab and copy the following:

- ✅ Account ID  
- ✅ Client ID  
- ✅ Client Secret  

You will need to add these values to your `.env` file:

```ini
ZOOM_ACCOUNT_ID=YOUR_ACCOUNT_ID
ZOOM_CLIENT_ID=YOUR_CLIENT_ID
ZOOM_CLIENT_SECRET=YOUR_CLIENT_SECRET
