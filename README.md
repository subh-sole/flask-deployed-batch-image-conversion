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
python -m pip install -r requirements.txt
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

## Deploy to AWS Elastic Beanstalk

This workflow runs from PowerShell on your Windows computer. You do not need to open a terminal in the AWS console: the AWS CLI and EB CLI use your local credentials to communicate with AWS, package the project, and deploy it. The project includes a `Procfile` that starts Flask with Gunicorn and a `requirements.txt` that tells Elastic Beanstalk which Python packages to install.

### Prerequisites

- An AWS account with permission to create and manage Elastic Beanstalk environments and their supporting resources. AWS may charge for those resources.
- Python and pip installed on your computer.
- The AWS CLI v2 and Elastic Beanstalk CLI (EB CLI) installed on your computer.

### 1. Install the AWS CLI

Download and run the AWS CLI v2 installer for Windows from the [official AWS instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Open a new PowerShell window and verify it is available:

```powershell
aws --version
```

### 2. Configure AWS access

Use the credentials or sign-in method provided by your AWS administrator. For an access key, configure the AWS CLI and enter the key, secret, and default AWS region when prompted:

```powershell
aws configure
aws sts get-caller-identity
```

Never put access keys in the project, README, or GitHub. If your organization uses AWS IAM Identity Center (SSO), use the sign-in flow provided by your administrator instead of creating an access key.

### 3. Install the EB CLI

Install EB CLI with Python's package installer:

```powershell
python -m pip install --user --upgrade awsebcli
```

Verify it:

```powershell
eb --version
```

If PowerShell says `eb` is not recognized, add Python's user `Scripts` directory to your Windows user `Path`, then open a new PowerShell window and try `eb --version` again. You can print the directory with:

```powershell
$PythonUserBase = python -m site --user-base
Join-Path $PythonUserBase "Scripts"
```

### 4. Initialize and create the Elastic Beanstalk environment

Go to the project root on your computer:

```powershell
cd "D:\conversionsit"
```

Initialize the EB CLI configuration for this project:

```powershell
eb init
```

Follow the prompts to choose the AWS region, create or select an Elastic Beanstalk application, and select a Python platform. This creates local EB CLI configuration for the project. Then create an environment (choose an environment name when prompted):

```powershell
eb create
eb open
```

`eb create` creates the AWS environment and performs the first deployment. The EB CLI uploads the application from your local project folder; pushing code to GitHub does not itself deploy it. Make sure `app.py`, `Procfile`, `requirements.txt`, `templates/`, and `static/` are in the project.

### 5. Deploy updates from your computer

After changing the app, run this from the same project folder:

```powershell
eb deploy
```

To open the deployed app again:

```powershell
eb open
```

Useful commands for checking a deployment:

```powershell
eb status
eb health
eb logs
```

### Remove the environment

When you no longer need the deployment, terminate the environment to avoid ongoing AWS charges:

```powershell
eb terminate
```

Follow the CLI prompts carefully; terminating the environment removes its running application resources.

---

## GitHub-ready project notes

Before uploading to GitHub, keep only the useful project files and ignore the temporary runtime data.

### Recommended keep list
- app.py
- Procfile
- requirements.txt
- templates/
- static/
- README.md
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
python -m pip install -r requirements.txt
python app.py
```

For the first AWS deployment, install AWS CLI v2 and EB CLI, configure AWS access, then run these commands locally from the project folder:

```powershell
python -m pip install awsebcli --upgrade --user
aws configure
aws sts get-caller-identity
eb --version
eb init
eb create
eb open
```

For each later deployment, use `eb deploy`.

---

## Final note

This app started as a local Flask image converter and later included AWS Elastic Beanstalk deployment steps. For local use, run it with Flask. For remote deployment, use the EB CLI workflow above.

This is a small, practical image conversion app and is suitable for GitHub once the duplicate backup files and runtime folders are cleaned up.
