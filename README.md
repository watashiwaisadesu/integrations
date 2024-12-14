# Integrations

# Table of Contents

1. [Introduction](#introduction)  
2. [Step-by-Step Guide: Setting up Instagram Integration](#step-by-step-guide-setting-up-instagram-integration) 
3. [Getting Started](#getting-started)  
   - [Setup Using Docker](#setup-using-docker)  
   - [Manual Setup](#manual-setup)  


## Introduction

This service integrates **_Instagram_**, **_WhatsApp_**, and **_Telegram_** into your application. 

It simplifies the configuration process by automating repetitive tasks and provides a seamless way to interact with users through these platforms.

Project Integrations is a backend service built with:
- **_Python_**
- **_FastAPI_**
- **_PostgreSQL_**
- **_SQLAlchemy_**
- **_Redis_**
- **_Celery_**.
- **_Docker_**


## Step-by-Step Guide: Setting up Instagram Integration

#### 1. Create an App on the Facebook Developer Console

First, you'll need to manually create an app on the platform:
[Facebook Developer Console](https://developers.facebook.com/apps/)

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/5935d6d6-b80f-486f-acd7-2dfc223dc051" alt="createapp" width="400">
</div>

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/f5b271a2-ad1d-486f-9c13-1552b913c946" alt="Screenshot" width="300" height="150">
  <img src="https://github.com/user-attachments/assets/74d7f319-1b58-46c6-acbf-36121556e791" alt="createapp" width="300">
  <img src="https://github.com/user-attachments/assets/5020ce4c-472c-4649-b58b-094ea24ab6e5" alt="Screenshot" width="300">
</div>

#### 2. Configure Products in the App
After creating the app, you need to enable the **Webhook Product** and **Instagram API Product**:

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/788dc969-e631-4238-9927-dad5ca4d583b" width="300">
  <img src="https://github.com/user-attachments/assets/cd511ce3-a59f-4eef-a045-4ad605896e2b" alt="Screenshot" width="300">
</div>

#### 3. Update App Settings and Turn on Live Mode
Next, go to the **App Settings** section in the left sidebar, fill out the required form fields, and turn on **Live Mode** for your app:

<img src="https://github.com/user-attachments/assets/432f575e-5204-4a60-b679-f8ad8725f284" width="400">

#### 4. Add Instagram Tester Accounts
For now, skip the app verification process to make your app publicly available. Instead, add Instagram tester accounts by username:

<img src="https://github.com/user-attachments/assets/ac9a0462-86a0-4804-a5dc-ac86b7f0b3fb" width="400">

#### 5. Grant Permissions
Once you’ve added the Instagram tester account, you’ll be asked to grant permissions. This step is essential to ensure access to the required APIs.

<img src="https://github.com/user-attachments/assets/f984ef9d-e901-4f52-9906-6ba4f25eb26e" width="400">

#### 6. Make Requests to the Instagram Endpoint
Finally, run the provided script and make a request to the following endpoint:
```
{domain}/v1/instagram/automation
```
**Note**: Replace {domain} with the appropriate domain of your backend application.

**Key Notes:**
- This is a one-time manual setup step and is not yet automated. 😄
- Be sure to double-check that your app is in Live Mode and properly configured.




## Getting Started

#### Clone the repository:

To get started, clone the repository from GitHub:

```bash
git clone https://github.com/watashiwaisadesu/integrations.git
cd your-repository
```

### Using DOCKER

#### 1. Create `.env` file

Create a `.env` file in the root directory of your project with the following content:

```env
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SYNC_DATABASE_URL=postgresql://username:password@localhost:5432/db_name
REDIS_URL=redis://redis:6379/0
```

This file is necessary for the application to run correctly.

#### 2. Running with Docker

Ensure **Docker** and **Docker Compose** are installed on your system.

Run the application using Docker Compose:

```bash
docker-compose up --build
```

#### 3. What This Command Does:
- Build the Docker images.
- Start the backend application.
- Set up the database and other dependencies (e.g., Redis).
  
#### 4. Access the application:

Once the application is running, you can access it in your browser at:

http://localhost:8000/v1/docs

### Manual Setup
If you prefer to set up the application without Docker, follow these steps:

#### 1. Install Dependencies
Make sure you have **Python 3.11+** installed. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configure the Environment
Create a `.env` file in the root directory with the following variables:

```env
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SYNC_DATABASE_URL=postgresql://username:password@localhost:5432/db_name
REDIS_URL=redis://localhost:6379/0
```

#### 3. Run Database Migrations
Initialize the database schema using Alembic:
```bash
alembic upgrade head
```
#### 4. Start the Application
Run the application:
```bash
uvicorn app.main:app 
```
also run in new terminal
```bash
celery -A src.core.celery_setup worker --loglevel=INFO
```
#### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
