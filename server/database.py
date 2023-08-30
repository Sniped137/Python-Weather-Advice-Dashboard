# Import necessary libraries
import re, random, supabase, uuid, configparser

# Read configuration data from a file
config = configparser.ConfigParser()
config.read('config.ini')

# Get Supabase URL and API key from the configuration file
supabase_url = config.get('Supabase', 'url')
supabase_key = config.get('Supabase', 'key')

# Create a Supabase client instance
client = supabase.create_client(supabase_url, supabase_key)

# Check if an email address is valid and not already in use
def is_valid_email(email):
    response = client.table('user_details').select("email").eq('email', email).execute()
    try:
        # If the email address already exists in the database, return an error message
        response.data[0]['email']
        return "Email address already exists"
    except:
        # Otherwise, check if the email address is valid and return an error message if not
        if len(email) == 0:
            return 'Email address field cannot be empty'
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return 'Email address is not valid'
        return None

# Check if a username is valid and not already in use
def is_valid_username(username):
    response = client.table('user_details').select("username").eq('username', username).execute()
    try:
        # If the username already exists in the database, return an error message
        response.data[0]['username']
        return "Username already exists"
    except:
        # Otherwise, check if the username is valid and return an error message if not
        if len(username) == 0:
            return 'Username field cannot be empty'
        if not re.match('^[a-zA-Z0-9]+$', username):
            return 'Username must contain only letters and numbers'
        if len(username) < 4:
            return 'Username must be at least 4 characters long'
        return None

# Check if a password meets the required complexity criteria
def is_valid_password(password):
    if len(password) == 0:
        return 'Password field cannot be empty'
    if not re.match('^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$', password):
        return 'Password requirements below not met'
    return None

# Check if the user has accepted the terms and conditions
def is_checkbox_checked(checkbox):
    if checkbox == 'off':
        return 'You have to accept T&Cs to proceed'
    
# Register a new user in the database
def register_user(email, username, password, checkbox):
    # Check if the email, username, password, or checkbox fields contain errors
    email_error = is_valid_email(email)
    username_error = is_valid_username(username)
    password_error = is_valid_password(password)
    checkbox_error = is_checkbox_checked(checkbox)
    if email_error or username_error or password_error or checkbox_error:
        # If any errors were found, return a dictionary containing the error messages
        return {f'success': False, 'email_error': email_error, 'username_error' : username_error, 'password_error' : password_error,
         'checkbox_error' : checkbox_error}
    # If no errors were found, create a new user in the database and return a success message
    res = client.auth.sign_up({"email": email,"password": password})
    user_id = res.user.id
    client.table('user_details').insert({'user_id' : user_id, 'email' : email, 'username' : username}).execute()
    return {'success': True}

# Log in a user with their email and password
def login_user(email, password):
    try:
        # Sign in the user with their email and password
        data = client.auth.sign_in_with_password({"email": email, "password": password})
        user_id = data.user.id
        # Retrieve the user's username from the database and return it along with the success message
        response = client.table('user_details').select("username").eq('user_id', user_id).execute()
        username = response.data[0]['username']
        response = ({'success' : True, 'user_id': user_id, 'username' : username})
        return response
    except Exception as error:
        error = str(error)
        # If the user's email has not been confirmed, return an error message
        if error == 'Email not confirmed':
            response = ({'success' : False, 'email_error': 'Email not verified'})
            return response
        # If the user's email or password is invalid, return an error message
        if error == 'Invalid login credentials' or 'You must provide either an email or phone number and a password':
            response = ({'success' : False, 'password_error': 'Invalid email or password'})
            return response

# Retrieve the contents of a post with a given post ID
def get_post_contents_by_id(post_id):
    response = dict(client.table('posts').select('*').eq('post_id', post_id).execute())['data']
    return response

# Generate a unique post ID
def generate_post_id():
    unique = False
    try:
        # Retrieve a list of all post IDs in the database
        query = client.table('posts').select('post_id').execute()
        post_id_list = query.data
        # Generate a new post ID until a unique one is found
        while not unique:
            duplicate_found = False
            post_id = str(uuid.uuid4())[:8]
            for row in post_id_list:
                if row['post_id'] == post_id:
                    duplicate_found = True
            if not duplicate_found:
                unique = True
        return post_id
    except Exception as e:
        outputmessage = (f"Error generating the post id. Error: {e}", False)

# Retrieve a list of all posts in the database
def get_all_posts():
    posts = []
    non_duplicate_posts = []
    # Retrieve all posts from the database and add them to a list
    response = dict(client.table('posts').select('*').execute())['data']
    advice_posts = list(response)
    for post in advice_posts:
        # Remove any duplicate posts from the list
        if post not in non_duplicate_posts:
            non_duplicate_posts.append(post)
    # Add each post's title, description, post ID, author's username, and image to a new list and shuffle it
    for p in non_duplicate_posts:
        title, description, post_id, author_username, post_image = p['title'], p['description'], p['post_id'], p['author_username'], p['post_image']
        posts.append([title, description, post_id, author_username, post_image])
    random.shuffle(posts)
    return posts

# NON FUNCTIONAL PROOF OF CONCEPT STARTS HERE

# Store a new post in the database
def store_post_in_database(post_id, post_data):
    try:
        client.table('posts').insert({'post_id' : post_id}, post_data).execute()
        outputmessage = (f"Post Submitted with ID {post_id} successfully stored in database.", True)
        return outputmessage
    except Exception as e:
        outputmessage = (f"Error storing post with ID {post_id} in database: {str(e)}", False)
        return outputmessage
    
# NON FUNCTIONAL PROOF OF CONCEPT ENDS   HERE



