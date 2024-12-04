Integrations
This service integrates Instagram, WhatsApp, and Telegram into your application. It simplifies the configuration process by automating repetitive tasks and provides a seamless way to interact with users through these platforms.

Project Integrations is backend service built with Python, FastAPI, PostgreSQL, SQLAlchemy, Redis and Celery.


## Before Getting Started
# 1.Create an App Manually

First, you'll need to manually create an app on the platform (e.g., Facebook Developer Console) https://developers.facebook.com/apps/.
Enable the Webhook Product and Instagram API Product within the app.
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

API Docs: http://localhost:8000/v1/docs
Redoc: http://localhost:8000/v1/redoc

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
