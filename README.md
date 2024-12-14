# Integrations

This service integrates Instagram, WhatsApp, and Telegram into your application. It simplifies the configuration process by automating repetitive tasks and provides a seamless way to interact with users through these platforms.

Project Integrations is backend service built with Python, FastAPI, PostgreSQL, SQLAlchemy, Redis and Celery.


# Before Getting Started
### 1. Instagram Setup Manually 

First, you'll need to manually create an app on the platform (e.g., Facebook Developer Console) [https://developers.facebook.com/apps/](https://developers.facebook.com/apps/).
<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/5935d6d6-b80f-486f-acd7-2dfc223dc051" alt="createapp" width="300">
  <img src="https://github.com/user-attachments/assets/f5b271a2-ad1d-486f-9c13-1552b913c946" alt="Screenshot" width="300">
</div>
![2](https://github.com/user-attachments/assets/74d7f319-1b58-46c6-acbf-36121556e791)
======
![image](https://github.com/user-attachments/assets/5020ce4c-472c-4649-b58b-094ea24ab6e5)
======
Enable the Webhook Product and Instagram API Product within the app.
======
![image](https://github.com/user-attachments/assets/788dc969-e631-4238-9927-dad5ca4d583b)
======
![image](https://github.com/user-attachments/assets/cd511ce3-a59f-4eef-a045-4ad605896e2b)
======
Then you'll see in the left side bar App-Settings section, select and open it.
Then fillout form and make sure to turn on Live Mode.
![image](https://github.com/user-attachments/assets/432f575e-5204-4a60-b679-f8ad8725f284)
=====
For now skip part where you have to pass verification process for your app to become publicly available!
Here add Instagram tester account by username!
![image](https://github.com/user-attachments/assets/ac9a0462-86a0-4804-a5dc-ac86b7f0b3fb)
=====

Then here youll get ask for permission
![image](https://github.com/user-attachments/assets/f984ef9d-e901-4f52-9906-6ba4f25eb26e)
=====
Then run script and make request to this endpoint
{domain}/v1/instagram/automation

This is a one-time manual step, so it's not automated.


# Getting Started
You can run this project using Docker for convenience or set it up manually by installing dependencies.


# Create .env file

ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SYNC_DATABASE_URL=postgresql://username:password@localhost:5432/db_name

REDIS_URL=redis://redis:6379/0


# Running with Docker
Clone the repository:

Ensure Docker and Docker Compose are installed on your system.

Run the application using Docker Compose:

docker-compose up --build

This command will:
Build the Docker images.
Start the backend application.
Set up the database and other dependencies (e.g., Redis).
Access the application:


# Manual Setup
If you prefer to set up the application without Docker, follow these steps:

# 1. Install Dependencies
Make sure you have Python 3.11+ installed. Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# 2. Configure the Environment
Create a .env file in the root directory with the following variables:

ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name
SYNC_DATABASE_URL=postgresql://username:password@localhost:5432/db_name

REDIS_URL=redis://localhost:6379/0

# 3. Run Database Migrations
Initialize the database schema using Alembic:

alembic upgrade head

# 4. Start the Application
Run the application:

uvicorn app.main:app 

# License
This project is licensed under the MIT License - see the LICENSE file for details.
