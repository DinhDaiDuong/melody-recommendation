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
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/recommendations/<genre>', methods=['GET'])
def recommend_by_genre(genre):
    try:
        genre_songs = df[df['genre'].str.lower() == genre.lower()]
        if len(genre_songs) == 0:
            return jsonify({'error': 'Genre not found'}), 404
            
        recommendations = genre_songs.sample(n=min(5, len(genre_songs))).to_dict('records')
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 