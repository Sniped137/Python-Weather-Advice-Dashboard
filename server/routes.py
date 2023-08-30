# Import necessary libraries
from flask import Flask, render_template, request, session, redirect, url_for
from database import get_post_contents_by_id, generate_post_id, store_post_in_database, login_user, register_user, get_all_posts
from api import get_location, get_location_data, current_weather, five_day_forecast, forecast_pollution, current_pollution_indexes
from datetime import timedelta

# Create a Flask application instance
app = Flask(__name__, template_folder='../templates',static_folder='../static')

# Set a secret key to encrypt and secure the user session data
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# Set a lifetime for the user session data
app.permanent_session_lifetime = timedelta(days=7)

# Create an error handler for 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# Create a route to display weather information
@app.route('/', methods=['GET', 'POST'])
def weather():
    # Check if the user is logged in
    if not session.get('loggedin'):
        # if not, redirect them to the login page
        return redirect(url_for('login'))
    
    # initialize variables for the weather information to prevent errors
    search_results, hours, temps, country, name, day_list, day_info, pollution_indexes, aqi_indexes = (None,) * 9
    pollutants = []
    if request.method == 'POST':
        if 'search' in request.form:
            # Check if the user has submitted a search form
            location_input = request.form.get('location_search')
            # If so, get the search results
            if location_input:
                search_results = get_location(location_input)
                
        if 'selected_item' in request.form:
             # If the user has selected a location from the search results, get its data
            selected_item = request.form.get('selected_item')
            if selected_item:
                response = get_location_data(selected_item)
                latitude, longitude = response[0]['lat'], response[0]['lon']
                name, country = current_weather(latitude, longitude, selected_item) 
                weather_response, day_list, day_info, hours, temps = five_day_forecast(latitude, longitude, selected_item)
                pollution_indexes, pollutants = forecast_pollution(latitude, longitude, selected_item)  
                aqi_indexes = current_pollution_indexes(pollutants)
    # Render the weather template with the retrieved informatio
    return render_template('weather.html', search_results=search_results, name=name, country=country, 
    day_list=day_list, day_info=day_info, hours=hours, temps=temps, pollution_indexes=pollution_indexes, pollutants=pollutants, aqi_indexes=aqi_indexes)

# Create a route to display an overview of advice posts
@app.route('/advice')
def advice_overview():
    # Check if the user is logged in
    if not session.get('loggedin'):
        # if not, redirect them to the login page
        return redirect(url_for('login'))
    # get all of the advice posts from the database
    posts = get_all_posts()
    # Render the advice overview template with the retrieved posts
    return render_template('advice_overview.html', posts=posts)

# Create a route to display a single advice post based from post id
@app.route('/advice/post/<string:post_id>', methods=['GET', 'POST'])
def view_advice_post(post_id):
    # check if the user is logged in
    if not session.get('loggedin'):
        # if not, redirect them to the login page
        return redirect(url_for('login'))
    # Get the content of the requested advice post from the database
    response = get_post_contents_by_id(post_id)
    title, image_url, content = response[0]['title'], response[0]['post_image'], response[0]['content']
    # render the advice post template with the retrieved content
    return render_template('advice_post.html', title=title, image_url=image_url, content=content)

# NON FUNCTIONAL PROOF OF CONCEPT STARTS HERE
@app.route('/advice/create')
def create_advice_post():
    # check if the user has submitted a post form
    if request.method == 'POST':
        # If so, generate a new post ID and create a dictionary of post data from the form
        post_id = generate_post_id()
        post_data = {
        'post_id' : post_id,
        'title': request.form['title'],
        'description': request.form['description'],
        'content': request.form['content'],
        'upvotes' : 0,
        'author_username': session['username'],
        'author_image': session['profile_url'],
        'post_image': request.form['post_url'],
        }
        # Store the new post in the database and redirect to the advice overview page
        outputmessage = store_post_in_database(post_id, post_data)
        if outputmessage[1]: 
            return redirect(url_for('advice'))
        else:
            return render_template('create_article.html', outputmessage[0])
    # if the user has not submitted a post form, render the create advice post template
    return render_template('create_article.html')
# NON FUNCTIONAL PROOF OF CONCEPT END HERE


@app.route('/register', methods=['GET', 'POST'])
def register():
    response = {}
    # check if the user is already logged in
    if session.get('loggedin'):
        # if so, redirect them to the weather page
        return redirect(url_for('weather'))
    # check if the user has submitted a registration form
    if request.method == 'POST':
        # if so, create a new user with the form data
        email, username, password, checkbox = request.form['email'], request.form['username'], request.form['password'], request.form.get("checkbox", "off")
        response = register_user(email, username, password, checkbox)
        # if the registration is successful, redirect to the login page
        if response['success']:
            return redirect(url_for('login'))
    # if the user has not submitted a registration form, render the registration template
    return render_template('register.html', response=response)

@app.route('/login', methods=['GET', 'POST'])
def login():
    response = {}
    # Check if the user is already logged in
    if session.get('loggedin'):
        # if so, redirect them to the weather page
        return redirect(url_for('weather'))
    # Check if the user has submitted a login form
    if request.method == 'POST':
        # if so, log in the user with the form data
        email, password = request.form['email'], request.form['password']
        checkbox = request.form.get("checkbox", "off")
        response = login_user(email, password)
        if response['success']:
            # if the login is successful, set the session data and redirect to the weather page
            if checkbox == 'on':
                session.permanent = True
            else:
                session.permanent = False
            session['loggedin'] = True
            session['user_id'] = response['user_id']
            session['username'] = response['username']
            return redirect(url_for('weather'))
    # if the user has not submitted a login form, render the login template
    return render_template('login.html', response=response)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # check if the user is logged in
    if not session.get('loggedin'):
        # if not, redirect them to the login page
        return redirect(url_for('login'))
    # remove the session data and redirect to the login page
    session.pop('_permanent', None)
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/terms-conditions', methods=['GET', 'POST'])
def termsandconditions():

    # Render the terms and conditions template
    return render_template('termsandconditions.html')


if __name__ == '__main__':
    app.run(debug=True)

