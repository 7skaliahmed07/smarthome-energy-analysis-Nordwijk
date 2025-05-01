from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class Device(Base):
    """Table to store unique smart home devices."""
    __tablename__ = 'devices'
    device_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    loc = Column(String)
    level = Column(String)

class SmartThingsMessage(Base):
    """Table to store messages from SmartThings devices."""
    __tablename__ = 'smartthings_messages'
    message_id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.device_id'))
    epoch = Column(Integer)
    capability = Column(String)
    attribute = Column(String)
    value = Column(String)
    unit = Column(String)

class ElectricityUsage(Base):
    """Table to store electricity usage from P1e source."""
    __tablename__ = 'electricity_usage'
    reading_id = Column(Integer, primary_key=True)
    epoch = Column(Integer, unique=True)  # Ensure no duplicate timestamps
    t1_kwh = Column(Float)  # Low-cost hours
    t2_kwh = Column(Float)  # High-cost hours

class GasUsage(Base):
    """Table to store gas usage from P1g source."""
    __tablename__ = 'gas_usage'
    reading_id = Column(Integer, primary_key=True)
    epoch = Column(Integer, unique=True)  # Ensure no duplicate timestamps
    gas_m3 = Column(Float)

class Weather(Base):
    """Table to store weather data from OpenWeatherMap (optional)."""
    __tablename__ = 'weather'
    reading_id = Column(Integer, primary_key=True)
    epoch = Column(Integer, unique=True)  # Ensure no duplicate timestamps
    temperature = Column(Float)
    humidity = Column(Float)

class HomeMessagesDB:
    """Class to manage the smart home messages database."""
    def __init__(self, db_url):
        """Initialize the database with a SQLAlchemy URL."""
        self.db_url = db_url
        self.engine = None
        self.Session = None
        self.session = None
        self.connect()

    def connect(self):
        """Establish connection to the database."""
        try:
            self.engine = create_engine(self.db_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
        except SQLAlchemyError as e:
            raise Exception(f"Failed to connect to database: {e}")

    def close(self):
        """Close the database session."""
        if self.session:
            self.session.close()
            self.session = None
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def insert_device(self, name, loc, level):
        """Insert a device if it doesn't exist and return its ID."""
        device = self.session.query(Device).filter_by(name=name).first()
        if not device:
            device = Device(name=name, loc=loc, level=level)
            self.session.add(device)
            self.session.commit()
        return device.device_id

    def insert_smartthings(self, loc, level, name, epoch, capability, attribute, value, unit):
        """Insert a SmartThings message."""
        try:
            device_id = self.insert_device(name, loc, level)
            # Check for duplicate message (same device, epoch, capability, attribute)
            existing = self.session.query(SmartThingsMessage).filter_by(
                device_id=device_id, epoch=epoch, capability=capability, attribute=attribute
            ).first()
            if not existing:
                message = SmartThingsMessage(
                    device_id=device_id, epoch=epoch, capability=capability,
                    attribute=attribute, value=value, unit=unit
                )
                self.session.add(message)
                self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Failed to insert SmartThings message: {e}")

    def insert_electricity(self, epoch, t1_kwh, t2_kwh):
        """Insert an electricity usage record."""
        try:
            # Check for duplicate epoch
            existing = self.session.query(ElectricityUsage).filter_by(epoch=epoch).first()
            if not existing:
                record = ElectricityUsage(epoch=epoch, t1_kwh=t1_kwh, t2_kwh=t2_kwh)
                self.session.add(record)
                self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Failed to insert electricity usage: {e}")

    def insert_gas(self, epoch, gas_m3):
        """Insert a gas usage record."""
        try:
            # Check for duplicate epoch
            existing = self.session.query(GasUsage).filter_by(epoch=epoch).first()
            if not existing:
                record = GasUsage(epoch=epoch, gas_m3=gas_m3)
                self.session.add(record)
                self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Failed to insert gas usage: {e}")

    def insert_weather(self, epoch, temperature, humidity):
        """Insert a weather record (optional)."""
        try:
            # Check for duplicate epoch
            existing = self.session.query(Weather).filter_by(epoch=epoch).first()
            if not existing:
                record = Weather(epoch=epoch, temperature=temperature, humidity=humidity)
                self.session.add(record)
                self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Failed to insert weather data: {e}")

    def query_smartthings(self, capability=None, attribute=None, start_epoch=None, end_epoch=None):
        """Query SmartThings messages with optional filters."""
        query = self.session.query(SmartThingsMessage)
        if capability:
            query = query.filter_by(capability=capability)
        if attribute:
            query = query.filter_by(attribute=attribute)
        if start_epoch:
            query = query.filter(SmartThingsMessage.epoch >= start_epoch)
        if end_epoch:
            query = query.filter(SmartThingsMessage.epoch <= end_epoch)
        return query.all()

    def query_electricity(self, start_epoch=None, end_epoch=None):
        """Query electricity usage with optional time range."""
        query = self.session.query(ElectricityUsage)
        if start_epoch:
            query = query.filter(ElectricityUsage.epoch >= start_epoch)
        if end_epoch:
            query = query.filter(ElectricityUsage.epoch <= end_epoch)
        return query.all()

    def query_gas(self, start_epoch=None, end_epoch=None):
        """Query gas usage with optional time range."""
        query = self.session.query(GasUsage)
        if start_epoch:
            query = query.filter(GasUsage.epoch >= start_epoch)
        if end_epoch:
            query = query.filter(GasUsage.epoch <= end_epoch)
        return query.all()

    def query_weather(self, start_epoch=None, end_epoch=None):
        """Query weather data with optional time range."""
        query = self.session.query(Weather)
        if start_epoch:
            query = query.filter(Weather.epoch >= start_epoch)
        if end_epoch:
            query = query.filter(Weather.epoch <= end_epoch)
        return query.all()