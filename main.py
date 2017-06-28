#Worked with Brian Brakefield
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST','GET'])
def newpost():
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
        new_blog = Blog(post_title, post_body)
        db.session.add(new_blog)
        db.session.commit()

        blog_id = str(new_blog.id)
        
        return redirect('/blog'+ '?id=' + blog_id)
    
    else:
        return render_template('newpost.html',title="Create Post")

@app.route('/blog')
def blog():

    blog_id = request.args.get('id')
    if blog_id:
        selected_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('individual.html', selected_blog=selected_blog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

@app.route('/')
def index():
    return redirect('/blog')

if __name__ == '__main__':
    app.run()