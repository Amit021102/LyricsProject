from sqlalchemy import create_engine
from models import Base

# 👇 Replace with your real DB credentials
engine = create_engine('postgresql+pg8000://postgres:rya33rya@localhost:5432/lyrics_db')

# 👇 This line creates all the tables in your PostgreSQL database
Base.metadata.create_all(engine)

print("✅ Tables created successfully!")

# # DROP ALL TABLES
# Base.metadata.drop_all(engine)