from flask import Flask, jsonify, request
import requests, string

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

                predictedGenres = genrePredict(movie_plot)
                return jsonify({
                        "title": movie_title,
                        "plot": movie_plot,
                        "predicted_genres": predictedGenres[:3] #specifically show top three, if there are more than 3 genres with scores greater than 0
                        })
        else:
                return jsonify({"error": "The movie was not found. Please check to make sure you provided the correct spelling."}), 404


def genrePredict(movie_plot):

        #genre dictionaries
        genres = {
                "Horror": ["blood", "death", "dead", "kill", "killer", "bloody", "deadly", "weapon", "murder", "scare", "scary", "monster", "monsters", "scream", "screams", "screaming", "clown", "fear", "haunted", "demon", "demonic", "preys", "prey", "possess", "possesses", "entity", "victims", "victim", "murder", "slay", "slay", "slaughter", "slaughters", "assassinate", "massacre", "suspense", "tension", "mystery", "thriller", "killing", "killing spree", "occult"],
                "Comedy": ["funny", "laugh", "laughs", "joke", "jokes", "humor", "parody", "parodies", "comedy", "clown", "misadventures", "slapstick", "sarcastic", "absurd", "ironic", "mock", "spoof", "satire", "lighthearted", "quirky"],
                "Romance": ["love", "loving", "heart", "lovers", "romance", "romantic", "kiss", "couple", "couples", "affection", "date", "dating", "marry", "marriage", "partner", "wife", "husband", "ex", "girlfriend", "boyfriend", "divorce", "struggle", "relationship", "commitment", "longing", "passion", "heartbreak", "unrequited"],
                "Action": ["fight", "fights", "explosion", "explosions", "hero", "heroes", "battle", "war", "mission", "save", "doom", "disaster", "combat", "battle", "duel", "warfare", "confrontation", "disaster", "chase", "gun", "gunfight", "violence", "rescue", "adventure", "bravery", "thriller", "danger", "climax", "superhero", "saving", "villain", "villains"],
                "Fantasy": ["monster", "beast", "vampire", "vampires", "werewolf", "werewolves", "dragon", "dragons", "unicorn", "unicorns", "magic", "prince", "princess", "king", "queen", "wizard", "witch", "enchantment", "spell", "myth", "fairy", "elf", "dwarf", "goblin", "quest", "villain", "villains"],
                "Sci-fi": ["alien", "space", "spaceship", "ship", "robot", "future", "technology", "intergalactic", "extraterrestrial", "spacecraft", "laser", "galaxy", "celestial", "futuristic", "cyberpunk", "virtual", "future", "cybernetics", "virtual reality", "android", "nanotechnology", "artificial intelligence", "machine", "hologram", "dystopia", "post-apocalyptic", "terraforming", "bioengineering", "superhero"],
                "Mystery": ["murder", "murderer", "strange", "killed", "crime", "crimes", "weapon", "weapons", "mystery", "mysteries", "gun", "knife", "poison", "suspense", "tension", "mystery", "thriller", "detective", "investigation", "clue", "suspense", "secret", "unexplained", "whodunit", "enigma", "thriller", "conspiracy", "hidden", "identify", "case", "investigate", "investigates", "sleuth"],
                }
        
        #set up genre scores
        scores = {genre: 0 for genre in genres}

        #take plot summary, remove capitalization and split into list
        plotSumm = movie_plot.translate(str.maketrans('', '', string.punctuation)).lower().split()

        #Iterate through 
        for word in plotSumm:
                for genre, keyword_list in genres.items():
                        if word in keyword_list:
                                scores[genre]+=1

        #Only show scores greater than 0
        scores = {genre: score for genre, score in scores.items() if score > 0}

        #Order the scores from greatest to least
        orderedScores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return orderedScores;


if __name__ == '__main__':
        app.run(debug=True)