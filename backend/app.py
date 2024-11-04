from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def get_movies():
        api_key='f05530ca'

        response = requests.get(f'https://www.omdbapi.com/?i=tt3896198&apikey=f05530ca')
        return jsonify(response.json())

if __name__ == '__main__':
        app.run(debug=True)