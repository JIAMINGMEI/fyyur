#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jiamingmei@localhost:5432/fyyur'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Todo {self.id} {self.name} {self.city}>'

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_descriptions = db.Column(db.String(300))
    show = db.relationship('Show', backref='artist', lazy=True)
# TODO: implement any missing fields, as a database migration using
# Flask-Migrate

# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DataTime, default=datetime.today())
    artist_id = db.Column(
        db.Interger,
        db.ForeignKey('artist.id'),
        nuallable=False)
    venue_id = db.Column(
        db.Interger,
        db.ForeignKey('venue.id'),
        nuallable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.
    data = Venue.query.all()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"

    try:
        if search_term:
            selection = Venue.query.order_by(Venue.id).filter(
                Venue.name.like('%{}%'.format(search_term)))
            count = len(selection)

            response = {
                "count": count,
                "data": [{
                    "id": selection.id,
                    "name": selection.name,
                    "num_upcoming_shows": len(selection.show),
                }]
            }
            return render_template(
                'pages/search_venues.html',
                results=response,
                search_term=request.form.get(
                    'search_term',
                    ''))

    except BaseException:
        abort(404)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    result = Venue.query.filter(Venue.id == venue_id).one_or_none()

    data = list(filter(lambda d: d['id'] == venue_id, [result]))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook link', '')
    website_link = request.form.get('website_link', '')

    # TODO: modify data to be the data object returned from db insertion
    venue = Venue(name=name, city=city, state=state,
                  address=address, phone=phone, image_link=image_link,
                  facebook_link=facebook_link, website_link=website_link)

    venue = db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except BaseException:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    try:
        if search_term:
            selection = Artist.query.order_by(
                Artist.id).filter(
                Artist.name.like(
                    '%{}%'.format(search_term)))
            count = len(selection)

    response = {
        "count": count,
        "data": [{
            "id": selection.id,
            "name": selection.name,
            "num_upcoming_shows": selection.show,
        }]
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using
    # artist_id
    result = Artist.query.filter(Artist.id == artist_id).one_or_none()

    data = list(filter(lambda d: d['id'] == artist_id, result))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.image_link.data = artist.image_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    artist = Artist.query.get(artist_id)

    try:
        artist.name = request.form('name')
        artist.genres = request.form('genres')
        artist.city = request.form('city')
        artist.state = request.form('state')
        artist.phone = request.form('phone')
        artist.website = request.form('website')
        artist.facebook_link = request.form('facebook_link')
        artist.seeking_venue = request.form('seeking_venue')
        artist.image_link = request.form('image_link')
        db.session.commit()

    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.clost()
    if not error:
        flash('Yeaheee!Artist upated!')
    if error:
        flash('Oops!Artist can not be upated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(request.form, meta={'csrf': False})
    venue = Venue.query.get(venue_id)

    if form.validate():
        if venue:
            form.name.data = venue.name
            form.genres.data = venue.genres
            form.city.data = venue.city
            form.address.data = venue.address
            form.state.data = venue.state
            form.phone.data = venue.phone
            form.website.data = venue.website
            form.facebook_link.data = venue.facebook_link
            form.seeking_talent.data = venue.seeking_talent
            form.image_link.data = venue.image_link
            form.seeking_description = venue.seeking_description

        # TODO: populate form with values from venue with ID <venue_id>
            return render_template(
                'forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    venue = Venue.query.get(venue_id)

    try:
        venue.name = request.form('name')
        venue.genres = request.form('genres')
        venue.city = request.form('city')
        venue.address = request.form('address')
        venue.state = request.form('state')
        venue.phone = request.form('phone')
        venue.website = request.form('website')
        venue.facebook_link = request.form('facebook_link')
        venue.seeking_talent = request.form('seeking_talent')
        venue.seeking_description = request.form('seeking_description')
        venue.image_link = request.form('image_link')
        db.session.commit()

    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.clost()
    if not error:
        flash('Yeaheee!Venue upated!')
    if error:
        flash('Oops!Venue can not be upated!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False

    try:
        # called upon submitting the new artist listing form
        # TODO: insert form data as a new Venue record in the db, instead
        name = request.form.get('name', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        phone = request.form.get('phone', '')
        genres = request.form.get('genres', '')
        image_link = request.form.get('image_link', '')
        facebook_link = request.form.get('facebook link', '')
        website_link = request.form.get('website_link', '')
        seeking_description = request.form.get('seeking_description', '')

        # TODO: modify data to be the data object returned from db insertion
        artist = Artist(name=name, city=city, state=state,
                        phone=phone, genres=genres, image_link=image_link,
                        facebook_link=facebook_link,
                        seeking_descriptions=seeking_description,
                        website_link=website_link)

        db.session.add(artist)
        db.session.commit()

    except BaseException:
        error = False
        db.session.rollback()
        print(sys.exc_info())
    # on successful db insert, flash success
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    if error:
        flash(
            'An error occurred. Artist ' +
            request.form['name'] +
            ' could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.
    data = Show.query.all()

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    try:
        show = Show(
            venue_id=form.venue_id.data,
            artist_id=form.artist_id.data,
            start_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')

        # TODO: on unsuccessful db insert, flash an error instead.
    except ValueError as err:
        db.session.rollback()
        print(err)
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
