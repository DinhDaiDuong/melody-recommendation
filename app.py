from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load data
df = pd.read_csv('data.csv')
features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 
           'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
X = df[features].values

def is_vietnamese(text):
    # Check if text contains Vietnamese characters
    vietnamese_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
    return any(char in vietnamese_chars for char in str(text).lower())

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
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
        
        # Calculate similarity
        similarity = cosine_similarity(song_features, X)
        similar_indices = similarity[0].argsort()[-6:-1][::-1]
        
        # Get recommended songs
        recommendations = df.iloc[similar_indices].to_dict('records')
        
        # Filter recommendations to match the language of the input song
        input_song_name = data.get('songName', '')
        is_input_vietnamese = is_vietnamese(input_song_name)
        
        filtered_recommendations = []
        for rec in recommendations:
            if is_vietnamese(rec.get('name', '')) == is_input_vietnamese:
                formatted_rec = {
                    'songId': str(rec.get('id', '')),
                    'songName': str(rec.get('name', 'Unknown Song')),
                    'artistId': str(rec.get('artist_id', '')),
                    'artistName': str(rec.get('artists', 'Unknown Artist')),
                    'songImagePath': str(rec.get('image_url', '')),
                    'audioPath': str(rec.get('preview_url', '')),
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
                filtered_recommendations.append(formatted_rec)
        
        return jsonify(filtered_recommendations)
    except Exception as e:
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
            formatted_rec = {
                'songId': str(rec.get('id', '')),
                'songName': str(rec.get('name', 'Unknown Song')),
                'artistId': str(rec.get('artist_id', '')),
                'artistName': str(rec.get('artists', 'Unknown Artist')),
                'songImagePath': str(rec.get('image_url', '')),
                'audioPath': str(rec.get('preview_url', '')),
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