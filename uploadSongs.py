import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from lyricsProgram import process_song  # or from wherever process_song is defined

# Step 1: Connect to DB
engine = create_engine("postgresql+pg8000://postgres:rya33rya@localhost:5432/lyrics_db")
Session = sessionmaker(bind=engine)
session = Session()

# Step 2: Path to the lyrics file(s)
lyrics_dir = "lyrics"
for filename in os.listdir(lyrics_dir):
    if filename.endswith(".txt"):
        path = os.path.join(lyrics_dir, filename)
        print(f"Uploading {path}...")
        process_song(path, session)

# Step 3: Save changes
session.commit()

# Step 4: Close session
session.close()
