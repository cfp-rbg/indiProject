from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

api_key = 'f05530ca'

@app.route('/get-movie', methods=['GET'])
def get_movie():
        movie_name = request.args.get('title')

        if not movie_name:
                return jsonify({"error": "Movie's title was not provided."}), 400
        
        response = requests.get(f'http://www.omdbapi.com/?t={movie_name}&apikey={api_key}')
        data = response.json()

        if data.get('Response') == 'True':
                movie_title = data['Title']
                movie_plot = data['Plot']
                return jsonify({"title": movie_title, "plot": movie_plot})
        else:
                return jsonify({"error": "The movie was not found. Please check to make sure you provided the correct spelling."}), 404


if __name__ == '__main__':
        app.run(debug=True)