# Google API Setup Instructions

You need to set up Google API credentials before running the application. Here's how:

## Step 1: Create Google Cloud Project & Enable APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Sheets API

## Step 2: Create Service Account Credentials

1. Go to APIs & Services → Credentials
2. Click "Create Credentials" → "Service Account"
3. Fill in service account details
4. Download the JSON credentials file
5. Rename it to `credentials.json` and place it in the project root

## Step 3: Upload credentials.json

You need to place your `credentials.json` file in this directory:
```
/home/desops/google-sheets-combiner/credentials.json
```

You can:
- Use `scp` to copy from your local machine:
  ```bash
  scp /path/to/credentials.json desops@server:/home/desops/google-sheets-combiner/
  ```
- Or create the file manually:
  ```bash
  nano credentials.json
  # Paste your JSON content
  ```

## Step 4: Set File Permissions
```bash
chmod 600 credentials.json
```

## Step 5: Configure Your Google Sheets URLs

Edit the URLs file:
```bash
nano config/urls.txt
```

Add your actual Google Sheets URLs (one per line), for example:
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_1/edit
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_2/edit
```

## Important Notes:
- The service account needs access to your Google Sheets
- Share your sheets with the service account email address
- The first run will create a `token.json` file for OAuth tokens
