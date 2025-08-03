from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine('postgresql+pg8000://postgres:rya33rya@localhost:5432/lyrics_db')
Session = sessionmaker(bind=engine)

# CREATE ALL TABLES
# Base.metadata.create_all(engine)
# print("✅ Tables created successfully!")

# DROP ALL TABLES
# Base.metadata.drop_all(engine)