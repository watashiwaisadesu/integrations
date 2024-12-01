# cookies_utils.py

import json
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from src.db.models.cookie_model import Cookies  # Adjust the import path as necessary
import time


def save_cookies_to_db(db_session: Session, email: str, driver):
    """Save cookies to the database."""
    try:
        cookies = driver.get_cookies()  # Synchronous call
        cookies_json = json.dumps(cookies)

        stmt = select(Cookies).where(Cookies.email == email)
        result = db_session.execute(stmt)
        existing_record = result.scalar_one_or_none()

        if existing_record:
            existing_record.cookies_data = cookies_json
        else:
            cookie_record = Cookies(email=email, cookies_data=cookies_json)
            db_session.add(cookie_record)

        db_session.commit()
        print("Cookies saved to database.")
    except Exception as e:
        db_session.rollback()
        print(f"Failed to save cookies to database: {e}")
        raise


def load_cookies_from_db(db_session: Session, email: str, driver):
    """Load cookies from the database."""
    try:
        stmt = select(Cookies).where(Cookies.email == email)
        result = db_session.execute(stmt)
        cookie_record = result.scalar_one_or_none()

        if cookie_record and cookie_record.cookies_data:
            cookies = json.loads(cookie_record.cookies_data)
            driver.get('https://developers.facebook.com/')  # Synchronous call
            for cookie in cookies:
                driver.add_cookie(cookie)  # Synchronous call
            print("Cookies loaded from database.")
            time.sleep(1)
            return True
        else:
            print("No cookies found in database for this email.")
            return False
    except Exception as e:
        print(f"Failed to load cookies from database: {e}")
        raise
