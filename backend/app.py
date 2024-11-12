from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests, string
from data.dicts import genres

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

#store api key
api_key = 'f05530ca'

def get_data(movie_title, api_key):
       response = requests.get(f'http://www.omdbapi.com/?t={movie_title}&apikey={api_key}')
       if response.status_code == 200:
              return response.json()
       else:
              return None

@app.route('/get-movie', methods=['GET'])
def get_movie():
        movie_name = request.args.get('title')

        if not movie_name:
               return jsonify({"error": "No movie title given."}), 400

        movie = read_movie(movie_name)

        if movie: #If found in db, recalculate genres and update in database
               predictedGenres = genrePredict(movie.plot)
               update_movie(movie.id, predictedGenres)

               return jsonify({
                      "Title": movie.title,
                      "Plot": movie.plot,
                      "Predicted Genres": movie.predicted_genres
                      })
        
        #store api data into database, return it to frontend
        data = get_data(movie_name, api_key)
        if data and data.get('Response') == 'True':
                title = data['Title']
                plot = data['Plot']
                predictedGenres = genrePredict(plot)

                add_movie(data)
                movie = read_movie(title)
                if movie:
                       update_movie(movie.id, predictedGenres)
                       return jsonify({
                              "Title": movie.title,
                              "Plot": movie.plot,
                              "Predicted Genres": movie.predicted_genres
                       })
                
        else: #If entered movie title does not match any movie in the API
                return jsonify({"error": "The movie was not found. Please check to make sure you provided the correct spelling."}), 404

#genre prediction algorithm
def genrePredict(movie_plot):
        #set up genre scores
        scores = {genre: 0 for genre in genres}

        #take plot summary, remove capitalization and split into list
        plotSumm = movie_plot.translate(str.maketrans('', '', string.punctuation)).lower().split()

        #Iterate through plo, 
        for word in plotSumm:
                for genre, keyword_list in genres.items():
                        if word in keyword_list:
                                scores[genre]+=1

        #If all scores are 0, return string
        if all(score == 0 for score in scores.values()):
               return 0
        
        #Only show scores greater than 0
        scores = {genre: score for genre, score in scores.items() if score > 0}

        #Order the scores from greatest to least
        orderedScores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        predictedGenres = {genre: score for genre, score in orderedScores}
        return predictedGenres;
        

class Movie(db.Model):
    __tablename__ = 'movie_data'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    plot = db.Column(db.Text, nullable=False)
    predicted_genres = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Movie {self.title}>'
    
def add_movie(api_data):
       if api_data: #check if movie already exists in database. if not, add it
              existing = Movie.query.filter_by(title=api_data['Title']).first()
              
              if not existing:
                     movie = Movie(
                            title = api_data['Title'],
                            plot = api_data['Plot'],
                            predicted_genres = None)
                     db.session.add(movie)
                     db.session.commit()

def read_movie(title): #get and return movie data from database
       movie = Movie.query.filter_by(title=title).first()
       return movie

def update_movie(movie_id, predicted_genres): #specifically update movie genres, since they're the only thing being changed
       movie = Movie.query.get(movie_id)
       if movie:
              movie.predicted_genres = predicted_genres
              db.session.commit()
              return movie
       return None

if __name__ == '__main__':
        with app.app_context():
               db.create_all()
        app.run(debug=True)