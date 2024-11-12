import React, { useState } from 'react';
import Plot from 'react-plotly.js';

function App() {
  const [movieName, setMovieName] = useState('')
  const [movieData, setMovieData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  //handle user movie name submissions
  const handleSearch = async(movieName) => {
    if(!movieName) return
    setLoading(true)
    setError('')
  
  //Interact with backend to grab data
    try {
      const response = await fetch(`http://127.0.0.1:5000/get-movie?title=${movieName}`)
      const data = await response.json()

      if(response.ok) {
        setMovieData(data)
      } else {
        setError(data.error) //display error message if entered movie isn't found
      }
      setLoading(false)

    } catch(err) { //if frontend cannot pull movie data from backend, return error
      setLoading(false)
      setError("Could not get media data.")
    }
  };

  //create pie chart based on returned genre scores
  function Graph({predictedGenres}) {

    if(!predictedGenres|| Object.keys(predictedGenres).length === 0) { //if all scores = 0, display error
      return <p>There is not enough data in the plot to predict genres.</p>;
    }

    const genres = Object.keys(predictedGenres)
    const scores = Object.values(predictedGenres)

    return (
      <Plot
        data = {[
          {
            type: 'pie',
            labels: genres,
            values: scores,
            textinfo: 'none',
            hoverinfo: 'label+scores+percent',
          },
        ]}
        layout = {{
          title: 'Genre Probabilities',
          showlegend:true,
        }}
      />
    );
  }
  
  //display everything
  return (
      <div>
          <h1>Media Genre Guesser</h1>
          <input
            type = "text"
            value = {movieName}
            onChange = {(e) => setMovieName(e.target.value)}
            placeholder = "Enter media title"
          />

          <button onClick = {() => handleSearch(movieName)}>Search</button>

          {loading && <p>Loading...</p>}
          {error && <p>{error}</p>}

          {
            movieData && (
              <div>
                <h2>{movieData.Title}</h2>
                <p>Plot: {movieData.Plot}</p>

                <Graph
                  predictedGenres = {movieData['Predicted Genres']}
                />
              </div>
            )
          }
      </div>
  );
}


export default App;
