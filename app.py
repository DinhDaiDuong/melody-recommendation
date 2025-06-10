from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load data
df = pd.read_csv('data.csv')
features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 
           'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
X = df[features].values

def is_vietnamese(text):
    # Vietnamese character patterns
    vietnamese_pattern = re.compile(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]')
    return bool(vietnamese_pattern.search(str(text).lower()))

def get_audio_url(song_name, artist_name, preview_url):
    # Return Spotify preview URL if available, otherwise return empty string
    if pd.isna(preview_url) or preview_url == '':
        print(f"No preview URL available for {song_name}")
        return ''
    print(f"Using Spotify preview URL for {song_name}: {preview_url}")
    return preview_url

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        input_song_name = data.get('songName', '')
        is_input_vietnamese = is_vietnamese(input_song_name)
        
        print(f"Input song: {input_song_name}")
        print(f"Is Vietnamese: {is_input_vietnamese}")
        
        # Filter songs by language first
        if is_input_vietnamese:
            df_filtered = df[df['name'].apply(is_vietnamese)]
        else:
            df_filtered = df[~df['name'].apply(is_vietnamese)]
            
        if len(df_filtered) == 0:
            print("No songs found in the specified language")
            return jsonify([])
            
        # Get features for filtered songs
        X_filtered = df_filtered[features].values
        
        # Get input features
        song_features = np.array([[
            float(data['acousticness']),
            float(data['danceability']),
            float(data['energy']),
            float(data['instrumentalness']),
            float(data['liveness']),
            float(data['loudness']),
            float(data['speechiness']),
            float(data['tempo']),
            float(data['valence'])
        ]])
        
        # Calculate similarity only for filtered songs
        similarity = cosine_similarity(song_features, X_filtered)
        similar_indices = similarity[0].argsort()[-6:-1][::-1]
        
        # Get recommended songs
        recommendations = df_filtered.iloc[similar_indices].to_dict('records')
        
        # Format recommendations to match Song model
        formatted_recommendations = []
        for rec in recommendations:
            song_name = str(rec.get('name', 'Unknown Song'))
            artist_name = str(rec.get('artists', 'Unknown Artist'))
            preview_url = rec.get('preview_url', '')
            audio_url = get_audio_url(song_name, artist_name, preview_url)
            
            formatted_rec = {
                'songId': str(rec.get('id', '')),
                'songName': song_name,
                'artistId': str(rec.get('artist_id', '')),
                'artistName': artist_name,
                'songImagePath': str(rec.get('image_url', '')),
                'audioPath': audio_url,
                'genre': str(rec.get('genre', 'pop')),
                'acousticness': float(rec.get('acousticness', 0.0)),
                'danceability': float(rec.get('danceability', 0.0)),
                'energy': float(rec.get('energy', 0.0)),
                'instrumentalness': float(rec.get('instrumentalness', 0.0)),
                'liveness': float(rec.get('liveness', 0.0)),
                'loudness': float(rec.get('loudness', 0.0)),
                'speechiness': float(rec.get('speechiness', 0.0)),
                'tempo': float(rec.get('tempo', 0.0)),
                'valence': float(rec.get('valence', 0.0))
            }
            formatted_recommendations.append(formatted_rec)
        
        print(f"Found {len(formatted_recommendations)} recommendations")
        return jsonify(formatted_recommendations)
    except Exception as e:
        print(f"Error in recommend: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/recommend_by_genre', methods=['POST'])
def recommend_by_genre():
    try:
        data = request.json
        genre = data.get('genre', '').lower()
        
        # Filter songs by genre
        genre_songs = df[df['genre'].str.lower() == genre]
        if len(genre_songs) == 0:
            return jsonify({'error': 'Genre not found'}), 404
            
        # Get random sample of songs
        recommendations = genre_songs.sample(n=min(5, len(genre_songs))).to_dict('records')
        
        # Format recommendations to match Song model
        formatted_recommendations = []
        for rec in recommendations:
            song_name = str(rec.get('name', 'Unknown Song'))
            artist_name = str(rec.get('artists', 'Unknown Artist'))
            audio_url = get_audio_url(song_name, artist_name, '')
            
            formatted_rec = {
                'songId': str(rec.get('id', '')),
                'songName': song_name,
                'artistId': str(rec.get('artist_id', '')),
                'artistName': artist_name,
                'songImagePath': str(rec.get('image_url', '')),
                'audioPath': audio_url,
                'genre': str(rec.get('genre', 'pop')),
                'acousticness': float(rec.get('acousticness', 0.0)),
                'danceability': float(rec.get('danceability', 0.0)),
                'energy': float(rec.get('energy', 0.0)),
                'instrumentalness': float(rec.get('instrumentalness', 0.0)),
                'liveness': float(rec.get('liveness', 0.0)),
                'loudness': float(rec.get('loudness', 0.0)),
                'speechiness': float(rec.get('speechiness', 0.0)),
                'tempo': float(rec.get('tempo', 0.0)),
                'valence': float(rec.get('valence', 0.0))
            }
            formatted_recommendations.append(formatted_rec)
        
        return jsonify(formatted_recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 