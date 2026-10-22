# Batch Image Converter

This project is a Flask web app for converting image files in batches between common formats. It allows a user to upload multiple files, select a source format and target format, convert the files, and download the converted results as a ZIP archive.

The app is designed for local testing and also includes the AWS Elastic Beanstalk deployment workflow that was used previously.

---

## What this app does

- Upload multiple images at once
- Restrict uploads to the selected source format
- Convert between image types such as TIFF, JPEG, PNG, BMP, GIF, and WEBP
- Download all converted files as one ZIP
- Clear uploaded and converted files from the app folders
- Run locally in a browser

---

## Supported formats

- TIFF
- JPEG
- PNG
- BMP
- GIF
- WEBP

---

## Relevant project files

### Keep for the app
- app.py — main Flask application and conversion logic
- templates/index.html — web UI and upload form
- static/styles.css — styling for the page
- README.md — project documentation

### Runtime folders
- uploads/ — temporary uploaded files
- converted/ — generated converted files

These runtime folders are useful locally but should usually be ignored in GitHub.

### Optional local testing files
- test/ — sample image files used during testing

### Not part of the main app
- backup ZIP files
- duplicate app folders
- old archived copies of the project
- private credentials or secrets

These should not be committed to GitHub unless intentionally required.

---

## Local run instructions

### 1. Open a terminal in the project folder

```powershell
cd "D:\conversionsit"
```

### 2. Install dependencies

```powershell
python -m pip install flask pillow
```

### 3. Start the app

```powershell
python app.py
```

If Python is not recognized on your machine, try:

```powershell
py app.py
```

### 4. Open the site in a browser

```text
http://127.0.0.1:5000
```

---

## How to test the app locally

1. Select a source format such as TIFF or JPEG
2. Select a target format such as JPEG or PNG
3. Choose one or more matching files
4. Click Convert Files
5. Verify the conversion completes successfully
6. Download the ZIP archive
7. Use the Clear Files button to remove the uploaded and converted data

---

## Basic security checks included

This app includes some server-side validation before accepting uploaded files:

- file is not empty
- file size is under the allowed max
- selected file type matches the chosen source format
- file signature matches the expected image type
- file content is not obviously an executable or script payload
- file can be opened successfully by Pillow as a valid image

This is a lightweight safeguard and is not a full antivirus scanner, but it helps block obvious malicious or malformed uploads.

---

## AWS Elastic Beanstalk CLI setup

To access and use the AWS Elastic Beanstalk Command Line Interface (EB CLI), use the following steps.

### 1. Install Python and pip

Make sure Python is installed first.

```powershell
python --version
```

### 2. Install the EB CLI

```powershell
pip install awsebcli --upgrade --user
```

### 3. Configure AWS credentials

```powershell
aws configure
```

You will be asked for:
- AWS Access Key ID
- AWS Secret Access Key
- default region
- output format

These credentials come from your AWS IAM account in the AWS Console.

### 4. Verify installation

```powershell
eb --version
```

This should print the installed EB CLI version.

---

## AWS deployment commands

Run the following commands from the project root directory.

### Initialize the app

```powershell
eb init
```

This will prompt you to choose a region and select or create an application.

### Create an environment

```powershell
eb create
```

### Deploy the app

```powershell
eb deploy
```

### Open the app in the browser

```powershell
eb open
```

### Terminate the environment when no longer needed

```powershell
eb terminate
```

> Remember: EB CLI commands should be run in the root folder of the app where the Elastic Beanstalk configuration files are located.

---

## GitHub-ready project notes

Before uploading to GitHub, keep only the useful project files and ignore the temporary runtime data.

### Recommended keep list
- app.py
- templates/
- static/
- README.md
- requirements.txt (if added)
- .gitignore

### Recommended ignore list
- uploads/
- converted/
- *.zip
- __pycache__/
- .env
- duplicate folders and backup copies

---

## Example setup summary

```powershell
cd "D:\conversionsit"
python -m pip install flask pillow
python app.py
```

For AWS deployment:

```powershell
pip install awsebcli --upgrade --user
aws configure
eb --version
eb init
eb create
eb deploy
eb open
```

---

## Final note

This app started as a local Flask image converter and later included AWS Elastic Beanstalk deployment steps. For local use, run it with Flask. For remote deployment, use the EB CLI workflow above.

This is a small, practical image conversion app and is suitable for GitHub once the duplicate backup files and runtime folders are cleaned up.
