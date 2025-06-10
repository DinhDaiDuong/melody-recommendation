import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Initialize Spotify client
client_id = '072a23d92821498d90f7945145c0a468'  # Replace with your Spotify Client ID
client_secret = '8defc236baed4d57a40f4d9d412bfee7'  # Replace with your Spotify Client Secret
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_spotify_info(song_name, artist_name):
    try:
        # Search for the song
        query = f"track:{song_name} artist:{artist_name}"
        results = sp.search(q=query, type='track', limit=1)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            return {
                'preview_url': track['preview_url'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                'spotify_id': track['id']
            }
        return {'preview_url': '', 'image_url': '', 'spotify_id': ''}
    except Exception as e:
        print(f"Error getting Spotify info for {song_name}: {str(e)}")
        return {'preview_url': '', 'image_url': '', 'spotify_id': ''}

def main():
    # Read the CSV file
    df = pd.read_csv('data.csv')
    
    # Add new columns if they don't exist
    if 'preview_url' not in df.columns:
        df['preview_url'] = ''
    if 'image_url' not in df.columns:
        df['image_url'] = ''
    if 'spotify_id' not in df.columns:
        df['spotify_id'] = ''
    
    # Process each song
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"Processing song {index} of {len(df)}")
            # Save progress every 100 songs
            df.to_csv('data_updated.csv', index=False)
        
        # Get artist name (handle list format)
        artist_name = row['artists'].strip("[]'").split(',')[0]
        
        # Get Spotify info
        spotify_info = get_spotify_info(row['name'], artist_name)
        
        # Update row
        df.at[index, 'preview_url'] = spotify_info['preview_url']
        df.at[index, 'image_url'] = spotify_info['image_url']
        df.at[index, 'spotify_id'] = spotify_info['spotify_id']
        
        # Sleep to avoid rate limiting
        time.sleep(0.1)
    
    # Save final result
    df.to_csv('data_updated.csv', index=False)
    print("Done!")

if __name__ == "__main__":
    main() 