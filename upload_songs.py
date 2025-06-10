import pandas as pd
import requests
import firebase_admin
from firebase_admin import credentials, storage
import os
from urllib.parse import quote

# Initialize Firebase
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'melody-c1456.firebasestorage.app'
})

def download_and_upload_song(preview_url, song_name, artist_name):
    try:
        # Download song
        response = requests.get(preview_url)
        if response.status_code != 200:
            print(f"Failed to download {song_name}: {response.status_code}")
            return False

        # Create filename
        filename = f"{song_name}_{artist_name}".replace(' ', '_').lower()
        filename = ''.join(c for c in filename if c.isalnum() or c == '_')
        filename = f"{filename}.mp3"

        # Save temporarily
        temp_path = f"temp/{filename}"
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, 'wb') as f:
            f.write(response.content)

        # Upload to Firebase
        bucket = storage.bucket()
        blob = bucket.blob(f"song_files/{filename}")
        blob.upload_from_filename(temp_path)

        # Clean up
        os.remove(temp_path)
        print(f"Successfully uploaded {song_name}")
        return True

    except Exception as e:
        print(f"Error processing {song_name}: {str(e)}")
        return False

def main():
    # Read data
    df = pd.read_csv('data.csv')
    
    # Process each song
    for _, row in df.iterrows():
        if pd.isna(row['preview_url']):
            continue
            
        song_name = row['name']
        artist_name = row['artists'].strip("[]'").split(',')[0]  # Get first artist
        preview_url = row['preview_url']
        
        print(f"Processing {song_name} by {artist_name}")
        download_and_upload_song(preview_url, song_name, artist_name)

if __name__ == "__main__":
    main() 