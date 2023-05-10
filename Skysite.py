from flask import Flask, request, redirect, render_template, url_for, session
import requests
import json
import MySQLdb.cursors
import random as re
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from datetime import datetime

cities = []
threads = []

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'key'

app.config['MYSQL_HOST'] = 'tfalconPy57.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'tfalconPy57'
app.config['MYSQL_PASSWORD'] = 'Tr1st@n01'
app.config['MYSQL_DB'] = 'tfalconPy57$Users'
mysql = MySQL(app)



# This is the function to make an api call
def get_weather(zip, today, sevenDay):
    key = "RCFA2FC8DPYXDBMG75A4HRUXC"
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+zip+"/" + today + "/" + sevenDay + "?unitGroup=us&key=" + key + "&contentType=json"
    response = requests.get(url).json()
    return response

def verify_login(username, password):
    for user in user:
        if user['username'] == username and user['password'] == password:
            return True
    return False


def findDay(hour):
    date_string = hour
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    day_of_week = date_object.strftime('%A')
    return day_of_week

def getRange():
    import datetime

    # Get the current date
    current_date = datetime.date.today()

    # Create a list to store the next 7 dates
    next_7_days = []

    # Loop 7 times to get the next 7 dates
    for i in range(7):
        next_day = current_date + datetime.timedelta(days=i)
        next_7_days.append(next_day)

    # Print the list of dates
    print(next_7_days)
    today = str(next_7_days[0])
    sevenDay = str(next_7_days[-1])
    return today, sevenDay
'''
 Convert the 'data' list to a comma-separated string
data_str = ','.join(str(x) for x in user['data'])
'''

#Starting the app with login and validation, register that once done you are taken to dashboard.
@app.route('/')
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    current_user = ''
    user = ''
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        '''
        if verify_login(username, password, users):
        '''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s',(username,))
        userInfo = cursor.fetchone()
        if userInfo and bcrypt.check_password_hash(userInfo['hashed_password'], password):
            user = {
                'user_id':userInfo['user_id'],
                'username':userInfo['username'],
                'first_name':userInfo['name'],
                'password':userInfo['hashed_password'],
                'email':userInfo['email'],
                'gender': userInfo['gender'],
                'city':userInfo['location'],
                'data': userInfo['data'].split(',') if userInfo['data'] else []
            }

            current_user = user['username']
            session['current_user'] = current_user
            session['id'] = user['user_id']
            today, sevenDay = getRange()
            zip = user['city']
            city = createCity(zip, today, sevenDay)
            name = city['name']
            user['city'] = city['name']
            json_t = json.dumps(user)
            session['user'] = json_t
            result = checkIfThere(name)
            if result:
                pass
            else:
                user['data'].append(city)
                # database
            json_t = json.dumps(user)
            session['user'] = json_t
            session['cities'] = 'null'
            return render_template('homePage.html', city=city)
        else:
            return render_template("error.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    global user
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        cOR = request.form['city']
        gender = request.form['gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        userFind = cursor.fetchone()
        if userFind:
            msg = 'Account already exists!'
            return render_template('register.html', msg=msg)
        else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cursor.execute('INSERT INTO Users (name, username, hashed_password, email, gender, location) VALUES (%s, %s, %s, %s, %s, %s)', (first_name, username, hashed_password, email, gender, cOR))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

#this function gets the citys you search and add it to dashboard when dashboard is clicked on the nav
@app.route('/dashboard')
def dashboard():
    json_stuff = session['cities']
    if not json_stuff == 'null':
        cities = json.loads(json_stuff)
    else:
        cities = []
    place = session['user']
    user = json.loads(place)
    data = user['data']
    return render_template("dashboard.html", cities=cities, favs=data)

def createCity(zip, today, sevenDay):
    try:
        weather_data = get_weather(zip, today, sevenDay)
    except KeyError:
        return "Zip code not found"
    city = {
        'name': weather_data['resolvedAddress'],
        'visibility': weather_data['days'][0]['visibility'],
        'feels_like': weather_data['days'][0]['feelslike'],
        'humidity': weather_data['days'][0]['humidity'],
        'precip': weather_data['days'][0]['precip'],
        'wind_speed': weather_data['days'][0]['windspeed'],
        'weather_descriptions': weather_data['days'][0]['conditions'],
        'temperature': weather_data['days'][0]['temp'],
        'observation_time': weather_data['days'][0]['datetime'],
        'feels_like_min': weather_data['days'][0]['feelslikemin'],
        'feels_like_max': weather_data['days'][0]['feelslikemax'],
        'hours':[{'time': weather_data['days'][0]['hours'][0]['datetime'],
                  'temp': weather_data['days'][0]['hours'][0]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][0]['conditions']},
                  {'time': weather_data['days'][0]['hours'][1]['datetime'],
                  'temp': weather_data['days'][0]['hours'][1]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][1]['conditions']},
                  {'time': weather_data['days'][0]['hours'][2]['datetime'],
                  'temp': weather_data['days'][0]['hours'][2]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][2]['conditions']},
                  {'time': weather_data['days'][0]['hours'][3]['datetime'],
                  'temp': weather_data['days'][0]['hours'][3]['temp'],
                  'weather_descriptions':weather_data['days'][0]['hours'][3]['conditions']},
                  {'time': weather_data['days'][0]['hours'][4]['datetime'],
                  'temp': weather_data['days'][0]['hours'][4]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][4]['conditions']},
                  {'time': weather_data['days'][0]['hours'][5]['datetime'],
                  'temp': weather_data['days'][0]['hours'][5]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][5]['conditions']},
                  {'time': weather_data['days'][0]['hours'][6]['datetime'],
                  'temp': weather_data['days'][0]['hours'][6]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][6]['conditions']},
                  {'time': weather_data['days'][0]['hours'][7]['datetime'],
                  'temp': weather_data['days'][0]['hours'][7]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][7]['conditions']},
                  {'time': weather_data['days'][0]['hours'][8]['datetime'],
                  'temp': weather_data['days'][0]['hours'][8]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][8]['conditions']},
                  {'time': weather_data['days'][0]['hours'][9]['datetime'],
                  'temp': weather_data['days'][0]['hours'][9]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][9]['conditions']},
                  {'time': weather_data['days'][0]['hours'][10]['datetime'],
                  'temp': weather_data['days'][0]['hours'][10]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][10]['conditions']},
                  {'time': weather_data['days'][0]['hours'][11]['datetime'],
                  'temp': weather_data['days'][0]['hours'][11]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][11]['conditions']},
                  {'time': weather_data['days'][0]['hours'][12]['datetime'],
                  'temp': weather_data['days'][0]['hours'][12]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][12]['conditions']},
                  {'time': weather_data['days'][0]['hours'][13]['datetime'],
                  'temp': weather_data['days'][0]['hours'][13]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][13]['conditions']},
                  {'time': weather_data['days'][0]['hours'][14]['datetime'],
                  'temp': weather_data['days'][0]['hours'][14]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][14]['conditions']},
                  {'time': weather_data['days'][0]['hours'][15]['datetime'],
                  'temp': weather_data['days'][0]['hours'][15]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][15]['conditions']},
                  {'time': weather_data['days'][0]['hours'][16]['datetime'],
                  'temp': weather_data['days'][0]['hours'][16]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][16]['conditions']},
                  {'time': weather_data['days'][0]['hours'][17]['datetime'],
                  'temp': weather_data['days'][0]['hours'][17]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][17]['conditions']},
                  {'time': weather_data['days'][0]['hours'][18]['datetime'],
                  'temp': weather_data['days'][0]['hours'][18]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][18]['conditions']},
                  {'time': weather_data['days'][0]['hours'][19]['datetime'],
                  'temp': weather_data['days'][0]['hours'][19]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][19]['conditions']},
                  {'time': weather_data['days'][0]['hours'][20]['datetime'],
                  'temp': weather_data['days'][0]['hours'][20]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][20]['conditions']},
                  {'time': weather_data['days'][0]['hours'][21]['datetime'],
                  'temp': weather_data['days'][0]['hours'][21]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][21]['conditions']},
                  {'time': weather_data['days'][0]['hours'][22]['datetime'],
                  'temp': weather_data['days'][0]['hours'][22]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][22]['conditions']},
                  {'time': weather_data['days'][0]['hours'][23]['datetime'],
                  'temp': weather_data['days'][0]['hours'][23]['temp'],
                  'weather_descriptions': weather_data['days'][0]['hours'][23]['conditions']},],
        'days':[{'date': weather_data['days'][0]['datetime'],
                 'dOW': findDay(weather_data['days'][0]['datetime']),
                 'weather_descriptions': weather_data['days'][0]['conditions'],
                 'temp': weather_data['days'][0]['temp'],
                 'max': weather_data['days'][0]['tempmax'],
                 'min': weather_data['days'][0]['tempmin']},
                 {'date': weather_data['days'][1]['datetime'],
                 'dOW': findDay(weather_data['days'][1]['datetime']),
                 'weather_descriptions': weather_data['days'][1]['conditions'],
                 'temp': weather_data['days'][1]['temp'],
                 'max': weather_data['days'][1]['tempmax'],
                 'min': weather_data['days'][1]['tempmin']},
                 {'date': weather_data['days'][2]['datetime'],
                 'dOW': findDay(weather_data['days'][2]['datetime']),
                 'weather_descriptions': weather_data['days'][2]['conditions'],
                 'temp': weather_data['days'][2]['temp'],
                 'max': weather_data['days'][2]['tempmax'],
                 'min': weather_data['days'][2]['tempmin']},
                 {'date': weather_data['days'][3]['datetime'],
                 'dOW': findDay(weather_data['days'][3]['datetime']),
                 'weather_descriptions': weather_data['days'][3]['conditions'],
                 'temp': weather_data['days'][3]['temp'],
                 'max': weather_data['days'][3]['tempmax'],
                 'min': weather_data['days'][3]['tempmin']},
                 {'date': weather_data['days'][4]['datetime'],
                 'dOW': findDay(weather_data['days'][4]['datetime']),
                 'weather_descriptions': weather_data['days'][4]['conditions'],
                 'temp': weather_data['days'][4]['temp'],
                 'max': weather_data['days'][4]['tempmax'],
                 'min': weather_data['days'][4]['tempmin']},
                 {'date': weather_data['days'][5]['datetime'],
                 'dOW': findDay(weather_data['days'][5]['datetime']),
                 'weather_descriptions': weather_data['days'][5]['conditions'],
                 'temp': weather_data['days'][5]['temp'],
                 'max': weather_data['days'][5]['tempmax'],
                 'min': weather_data['days'][5]['tempmin']},
                 {'date': weather_data['days'][6]['datetime'],
                 'dOW': findDay(weather_data['days'][6]['datetime']),
                 'weather_descriptions': weather_data['days'][6]['conditions'],
                 'temp': weather_data['days'][6]['temp'],
                 'max': weather_data['days'][6]['tempmax'],
                 'min': weather_data['days'][6]['tempmin']}]
    }
    return city

## this is what happens when you add a city to your dashboard
@app.route('/app.py/getvalue', methods = ['GET','POST'])
def getvalue():
    json_stuff = session['cities']
    if not json_stuff == 'null':
        cities = json.loads(json_stuff)
    else:
        cities = []
    place = session['user']
    user = json.loads(place)

    zip = request.form['zip']
    today, sevenDay = getRange()
    cities_copy = cities.copy()
    ## i need to make sure duplicates arent made still not working
    for city in cities_copy:
        if city['name'] == zip:
            cities.remove(city)
            this = createCity(zip, today, sevenDay)
            cities.append(this)
            json_t = json.dumps(cities)
            session['cities'] = json_t

            # Add code to display a pop-up window with the name of the updated city


    # Add the new city to the list if it doesn't already exist
    city = createCity(zip, today, sevenDay)
    if city not in cities:
        cities.append(city)
        json_t = json.dumps(cities)
        session['cities'] = json_t
    data = user['data']
    return render_template("dashboard.html", cities=cities, favs=data)

def checkIfThere(name):
    json_a = session['user']
    user = json.loads(json_a)
    for i in user['data']:
        if i['name'] == name:
            return True
    return False


#idk why this function is not being called look at dashboard button link
@app.route('/addToUser/<name>')
def addToUser(name):
    print(name)
    json_stuff = session['cities']
    cities = json.loads(json_stuff)
    place = session['user']
    user = json.loads(place)
    for city in cities:
        if city['name'] == name:
            result = checkIfThere(name)
            if result:
                pass
            else:
                user['data'].append(city)
                data = user['data']
                json_t = json.dumps(user)
                session['user'] = json_t
                print(user)
    return render_template('dashboard.html', cities=cities, favs=data)

#when i click the button on the html page to add to user i gives error


#finish function
@app.route('/removeFromUser/<name>')
def removeFromUser(name):
    json_stuff = session['cities']
    cities = json.loads(json_stuff)
    place = session['user']
    user = json.loads(place)
    for i in user['data']:
        if i['name'] == name:
            user['data'].remove(i)
            data = user['data']
            json_t = json.dumps(user)
            session['user'] = json_t
    return render_template('dashboard.html', cities=cities, favs=data)

# this is the function that loads the community page and if no posts are made then it will display that
@app.route("/community", methods=["GET","POST"])
def community():
    book = []
    current_user = session['current_user']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from Threads')
    threads = cursor.fetchmany(1000)

    for row in threads:
        if row == []:
            break
        else:
            thread = {
                'temp': row['temp'],
                'conditions': row['conditions'],
                'name': row['name'],
                'likes': row['likes'] ,
                'likedBy':row['liked_by'],
                'content': row['content'],
                'comments':row['comment'] ,
                'city': row['city']
            }

            book.append(thread)
    if not book:
        return render_template("community.html", current_user=current_user)
    else:
        return render_template("community.html", threads = book, current_user=current_user)

#when a user clicks the submit button on the community page this function runs to post the post

@app.route("/postThread", methods=["POST", "GET"])
def postThread():
    book = []
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    city = user['city']
    today, sevenDay = getRange()
    weather_data = get_weather(city, today, sevenDay)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    temp = weather_data['days'][0]['temp']
    conditions = weather_data['days'][0]['conditions']
    name = current_user
    likes = 0
    likedBy = "null"
    content = request.form['content']
    comments = "null"
    cursor.execute('INSERT INTO Threads (temp, conditions, name, likes, liked_By, content, comment, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (temp, conditions, name, likes, likedBy, content, comments, city))
    mysql.connection.commit()

    cursor.execute('SELECT * from Threads')
    threads = cursor.fetchmany(1000)

    for row in threads:
        if row == []:
            break
        else:
            thread = {
                "temp": row['temp'],
                "conditions": row['conditions'],
                "name": row['name'],
                "likes": row['likes'] ,
                "likedBy":row['liked_by'],
                "content": row['content'],
                "comments":row['comment'] ,
                "city": row['city']
            }
            book.append(thread)
    return render_template("community.html", threads = book, current_user=current_user)#add the post to the beginning of the array for the threads


# this it the function for the home city that gets the city and parses it
@app.route('/homePage/<city>')
def homePage(city):
    city_dict = json.loads(city.replace("'", "\""))
    return render_template('homePage.html', city=city_dict) #temp page needs to be separate then normal homepage

#this function is only called when a user clicks the home link on nav
@app.route('/hP')
def hP():
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    if user['username'] == current_user:
        zip = user['city']
        today, sevenDay = getRange()
        this = createCity(zip, today, sevenDay) # i think i should remove the old one and append the new one
    return render_template('homePage.html', city=this)

# log out function
@app.route('/login/logout')
def logout():
    global current_user ## pop all
    global cities
    current_user = ''
    cities = ""
    return render_template('index.html')


@app.route('/post/<thread>')
def post(thread):
    thread = json.loads(thread.replace("'", "\""))
    current_thread = thread

    comments = current_thread['comments']
    """
    for i in comments:
        if i == []:
            comments.remove[i]
        else:
            pass
    """
    place = json.dumps(current_thread)
    session['current_thread'] = place
    current_thread['comments'] = comments
    return render_template('post.html', thread=thread)


@app.route('/comment', methods=["POST", "GET"])
def comment():
    current_user = session['current_user']
    place = session['current_thread']
    current_thread = json.loads(place)
    content = request.form['content']
    comment = current_user+ ": " + content

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Threads WHERE content = %s', (current_thread['content'],))
    userFind = cursor.fetchone()
    this = {
        "temp": userFind['temp'],
        "name": userFind['name'],
        "likes": userFind['likes'],
        "liked_by": userFind['liked_by'],
        "content": userFind['content'],
        "conditions": userFind['conditions'],
        "comment": userFind['comment'],
        "city": userFind['city']
        }
    why = this['comment']
    if why == 'null' or why == []:
        why = []
        why.append(comment)
    else:
        why = [why]
        why.append(comment)
    comments = why
    #comments = json.dumps(comments)
    cursor.execute('UPDATE Threads SET comment = %s WHERE content = %s', (comments, current_thread['content'],))
    cursor.connection.commit()
    #comments = json.loads(comments)
    return render_template('post.html', thread=current_thread, comments=comments)
    #return render_template('post.html', thread=current_thread, comments=comments)


@app.route('/like/<thread>')
def like(thread):
    global threads
    place = session['current_thread']
    current_thread = json.loads(place)
    current_user = session['current_user']
    thread = json.loads(thread.replace("'", "\""))
    current_thread = thread
    for thread in threads:
        if thread['content'] == current_thread['content']:
            if len(thread['likedBy']) > 0:
                for i in thread['likedBy']:
                    if i == current_user:
                        thread['likes'] -= 1
                        thread['likedBy'].remove(current_user)
                    else:
                        thread['likes'] += 1
                        thread['likedBy'].append(current_user)
            else:
                thread['likes'] += 1
                thread['likedBy'].append(current_user)
    return render_template('community.html', threads=threads, current_user=current_user)

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/settings')
def settings():
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    if user['username'] == current_user:
        account = user
    return render_template('settings.html', account=account)


@app.route('/change_username', methods=["POST","GET"])
def change_username():
    if request.method == 'POST':
        new_username = request.form.get('username')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Users SET username = %s WHERE user_id = %s', (new_username, session['id'],))
        cursor.connection.commit()
        cursor.close()
        place = session['user']
        user = json.loads(place)
        """
        addUsername = json.dumps(new_username)
        session['current_user'] = addUsername
        """
        session['current_user'] = new_username
        user['username'] = new_username
        current_user = session['current_user']
        if session['current_user'] == current_user:
            account = user
            json_sucks = json.dumps(user)
            session['user'] = json_sucks
        else:
            account = None
            json_sucks = json.dumps(user)
            session['user'] = json_sucks

    return render_template('settings.html',account=account)

@app.route('/change_first_name', methods=["POST", "GET"])
def change_first_name():
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    name = request.form['name']
    if session['current_user'] == current_user:
        user['first_name'] = name
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Users SET name = %s WHERE user_id = %s', (name, session['id'],))
        cursor.connection.commit()
        account = user
        json_t = json.dumps(user)
        session['user'] = json_t
    return render_template('settings.html', account=account)

@app.route('/change_password', methods=["POST", "GET"])
def change_password():
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    old = request.form['old']
    password = request.form['password']
    confirm = request.form['Confirm']
    msg = ''
    if user['username'] == current_user:
        if bcrypt.check_password_hash(user['password'], old):
            if password == confirm:
                password = bcrypt.generate_password_hash(password).decode('utf-8')
                user['password'] = password
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE Users SET hashed_password = %s WHERE user_id = %s', (password, session['id'],))
                cursor.connection.commit()
                account = user
                msg = 'New password set'
                json_t = json.dumps(user)
                session['user'] = json_t
            else:
                msg = "New passwords don't match"
                account = user
        else:
            msg = 'Old password not verified'
            account = user
    return render_template('settings.html', account=account, msg=msg)

@app.route('/change_email', methods=["POST", "GET"])
def change_email():
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    email = request.form['email']
    if user['username'] == current_user:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Users SET email = %s WHERE user_id = %s', (email, session['id'],))
        cursor.connection.commit()
        user['email'] = email
        account = user
        json_t = json.dumps(user)
        session['user'] = json_t
    return render_template('settings.html', account=account)

@app.route('/change_home_city', methods=["POST", "GET"])
def change_home_city():
    place = session['user']
    user = json.loads(place)
    current_user = session['current_user']
    zip = request.form['city']
    if user['username'] == current_user:
        today, sevenDay = getRange()
        city = createCity(zip, today, sevenDay)
        user['city'] = city['name']
        name = city['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE Users SET location = %s WHERE user_id = %s', (name, session['id'],))
        cursor.connection.commit()
        result = checkIfThere(name)
        if result:
            pass
        else:
            user['data'].append(city)
        account = user
        json_t = json.dumps(user)
        session['user'] = json_t
    return render_template('settings.html', account=account)
