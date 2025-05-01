from home_messages_db import HomeMessagesDB, Device, SmartThingsMessage, ElectricityUsage, GasUsage
from sqlalchemy.exc import SQLAlchemyError

def test_database():
    try:
        # Initialize the database
        db = HomeMessagesDB('sqlite:///myhMy shoes. Hey. Hey, Cortana. Cortana. Hey. Hey, Cortana. Hey, Cortana. Hey, Cortana. Hey, Cortana. Hey, Cortana. Hey, Cortana. Download. Make back the happen we should allow me. To get three hours of games. Hey, Cortana. Open any. Hey, Cortana. Play. I. Hey, Cortana. Hey, hey, hey. Woah, Ferengi. Go. I. Hey, Cortana. ome.db')
        print("Database initialized successfully.")

        # Insert a device
        device_id = db.insert_device(name="Kitchen (table)", loc="kitchen", level="ground")
        print(f"Inserted device with ID: {device_id}")

        # Insert a SmartThings message
        db.insert_smartthings(
            loc="kitchen", level="ground", name="Kitchen (table)", epoch=1665386804,
            capability="switch", attribute="switch", value="off", unit=""
        )
        print("Inserted SmartThings message.")

        # Insert an electricity usage record
        db.insert_electricity(epoch=1665386804, t1_kwh=7937.977, t2_kwh=6284.179)
        print("Inserted electricity usage.")

        # Insert a gas usage record
        db.insert_gas(epoch=1665386804, gas_m3=123.456)
        print("Inserted gas usage.")

        # Query devices
        devices = db.session.query(Device).all()
        print("\nDevices in database:")
        for device in devices:
            print(f"ID: {device.device_id}, Name: {device.name}, Loc: {device.loc}, Level: {device.level}")

        # Query SmartThings messages
        messages = db.query_smartthings()
        print("\nSmartThings messages:")
        for msg in messages:
            print(f"ID: {msg.message_id}, Device ID: {msg.device_id}, Epoch: {msg.epoch}, Value: {msg.value}")

        # Query electricity usage
        elec = db.query_electricity()
        print("\nElectricity usage:")
        for record in elec:
            print(f"ID: {record.reading_id}, Epoch: {record.epoch}, T1: {record.t1_kwh}, T2: {record.t2_kwh}")

        # Query gas usage
        gas = db.query_gas()
        print("\nGas usage:")
        for record in gas:
            print(f"ID: {record.reading_id}, Epoch: {record.epoch}, Gas: {record.gas_m3}")

        # Close the connection
        db.close()
        print("Database connection closed.")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    test_database()