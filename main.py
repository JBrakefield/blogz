from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.route("/login", methods=['GET', 'POST'])
def login():
    login_error = ''
    if request.method == 'GET':
        return render_template('login.html', login_error=login_error)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                return redirect("/newpost")
            else:
                login_error = 'Incorrect password.'
        else:
            login_error = 'Incorrect username.'
        return render_template('login.html', login_error=login_error)

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    username_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #Validate username
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            username_error = 'That username is already taken.'
            return render_template('signup.html', username_error=username_error, password_error=password_error)
        if len(username) < 3:
            username_error = 'Username must be longer than 3 characters.'
            return render_template('signup.html', username_error=username_error, password_error=password_error)
        #Validate password
        if len(password) < 3:
            password_error = 'Password must be longer than 3 characters.'
            return render_template('signup.html', username_error=username_error, password_error=password_error)
        if password != verify:
            password_error = 'Passwords must match.'
        #Create new user
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/newpost")
    else:
        return render_template('signup.html', username_error=username_error, password_error=password_error)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    owner = User.query.filter_by(username=session['user']).first()
    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        #initiate errors and verify title and body are not empty
        title_error = ''
        body_error = ''
        if len(post_title) == 0:
            title_error = 'Your post must have a title.'
            return render_template('newpost.html', title="Create Post", 
                post_title=post_title, post_body=post_body, title_error=title_error)
        if len(post_body) == 0:
            body_error = 'Your post must have a body.'
            return render_template('newpost.html', title="Create Post", 
                post_title=post_title, post_body=post_body, body_error=body_error)
        new_blog = Blog(post_title, post_body, owner)
        db.session.add(new_blog)
        db.session.commit()

        blog_id = str(new_blog.id)
        
        return redirect('/blog'+ '?id=' + blog_id)
    
    else:
        return render_template('newpost.html',title="Create Post")

@app.route('/blog')
def blog():

    blog_id = request.args.get('id')
    user_name = request.args.get('user')
    if blog_id:
        selected_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('individual.html', selected_blog=selected_blog)
    elif user_name:
        selected_user = User.query.filter_by(username=user_name).first()
        blogs = Blog.query.filter_by(owner_id=selected_user.id).all()
        return render_template('singleUser.html', selected_user = selected_user, blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog', 'individual', 'singleUser','logout']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/index')
def index():
    username = request.args.get('username')
    if username:
        selected_user = User.query.filter_by(username=username).first()
        return render_template('singleUser.html')
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()