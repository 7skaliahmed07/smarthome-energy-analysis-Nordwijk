# create_db.py
from home_messages_db import HomeMessagesDB


def create_database():
    db = HomeMessagesDB('sqlite:///smarthome.db')
    print("Wow...Database created successfully:---> smarthome.db")
    db.close()


if __name__ == "__main__":
    print("Creating database...")
    create_database()
