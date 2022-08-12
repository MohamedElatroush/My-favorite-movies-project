from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

TMDB_API = "4505d63c854a465ddc1e99a5887fb3b1"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

class ReviewForm(FlaskForm):
    rating = FloatField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(300), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(400), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)

db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    print(all_movies)
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        params = {
            "api_key": TMDB_API,
            "query": movie_title
        }
        URL = "https://api.themoviedb.org/3/search/movie"
        response = requests.get(URL, params=params)
        response.raise_for_status()
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)

@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    print(movie_api_id)
    if movie_api_id:
        url = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        tmdb_img_url = f"https://image.tmdb.org/t/p/original/"
        params = {
            "api_key": TMDB_API,
            "language": "en-US"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(data['poster_path'])
        new_movie = Movie(
            title=data['title'],
            year=data['release_date'].split("-")[0],
            img_url=f'{tmdb_img_url}{data["poster_path"]}',
            description=data['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("reviewPage", id=new_movie.id))

@app.route('/edit', methods=["GET", "POST"])
def reviewPage():
    form = ReviewForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)



if __name__ == '__main__':
    app.run(debug=True)
