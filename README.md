# Integrations

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


# Before Getting Started
### 1. Instagram Setup Manually 

First, you'll need to manually create an app on the platform (e.g., Facebook Developer Console) 
[https://developers.facebook.com/apps/](https://developers.facebook.com/apps/).

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/5935d6d6-b80f-486f-acd7-2dfc223dc051" alt="createapp" width="300">
</div>

Then ->

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/f5b271a2-ad1d-486f-9c13-1552b913c946" alt="Screenshot" width="300" height="150">
  <img src="https://github.com/user-attachments/assets/74d7f319-1b58-46c6-acbf-36121556e791" alt="createapp" width="300">
  <img src="https://github.com/user-attachments/assets/5020ce4c-472c-4649-b58b-094ea24ab6e5" alt="Screenshot" width="300">
</div>

Enable the Webhook Product and Instagram API Product within the app.

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/788dc969-e631-4238-9927-dad5ca4d583b" width="300">
  <img src="https://github.com/user-attachments/assets/cd511ce3-a59f-4eef-a045-4ad605896e2b" alt="Screenshot" width="300">
</div>

Then you'll see in the left side bar App-Settings section, select and open it.
Then fillout form and make sure to turn on Live Mode.

<img src="https://github.com/user-attachments/assets/432f575e-5204-4a60-b679-f8ad8725f284" width="400">

For now skip part where you have to pass verification process for your app to become publicly available!
Here add Instagram tester account by username!

<img src="https://github.com/user-attachments/assets/ac9a0462-86a0-4804-a5dc-ac86b7f0b3fb" width="400">


Then here youll get ask for permission

<img src="https://github.com/user-attachments/assets/f984ef9d-e901-4f52-9906-6ba4f25eb26e" width="400">

Then run script and make request to this endpoint

{domain}/v1/instagram/automation

This is a one-time manual step, so it's not automated.  😄




# Getting Started

## - Clone the repository:

To get started, clone the repository from GitHub:

```bash
git clone https://github.com/watashiwaisadesu/integrations.git
cd your-repository
```

## Using DOCKER

### 1. Create `.env` file

Create a `.env` file in the root directory of your project with the following content:

```env
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SYNC_DATABASE_URL=postgresql://username:password@localhost:5432/db_name
REDIS_URL=redis://redis:6379/0
```

This file is necessary for the application to run correctly.

### 2. Running with Docker

Ensure **Docker** and **Docker Compose** are installed on your system.

Run the application using Docker Compose:

```bash
docker-compose up --build
```

### 3. What This Command Does:
- Build the Docker images.
- Start the backend application.
- Set up the database and other dependencies (e.g., Redis).
  
### 4. Access the application:

Once the application is running, you can access it in your browser at:

http://localhost:8000/v1/docs

## Manual Setup
If you prefer to set up the application without Docker, follow these steps:

### 1. Install Dependencies
Make sure you have **Python 3.11+** installed. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure the Environment
Create a `.env` file in the root directory with the following variables:

```env
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SYNC_DATABASE_URL=postgresql://username:password@localhost:5432/db_name
REDIS_URL=redis://localhost:6379/0
```

### 3. Run Database Migrations
Initialize the database schema using Alembic:
```bash
alembic upgrade head
```
### 4. Start the Application
Run the application:
```bash
uvicorn app.main:app 
```
In new terminal
```bash
celery -A src.core.celery_setup worker --loglevel=INFO
```
### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
