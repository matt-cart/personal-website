import markdown
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from website import app, db, login_manager, bcrypt
from website.models import Post, User
from flask import render_template, request, url_for, redirect
from flask.ext.login import login_required, login_user, logout_user, current_user


def parseDate(sql_date):
    date_object = datetime.strptime(str(sql_date).split(' ')[0], '%Y-%m-%d')
    return date_object.strftime('%B %d, %Y')


def parsePostQuery(posts):
    post_previews = []
    for post in posts:
        html = markdown.markdown(post.content)
        html_text = BeautifulSoup(html).findAll(text=True)
        text_preview = ''.join(html_text)[:200] + '...'
        post_previews.append({'title': post.title,
                              'preview': text_preview,
                              'date': parseDate(post.date),
                              'url_path': post.url_path})
    return post_previews


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


@app.route('/')
def index():
    three_posts = Post.query.filter(
        Post.status == 'published').order_by(Post.id.desc()).limit(3)
    recent_posts = parsePostQuery(three_posts)
    return render_template('home_page.html',
                           recent_posts=recent_posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    """For GET requests, display the login form. For POSTS, login the current
    user by processing the form."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter(User.email == username).first()
        if username:
            if bcrypt.check_password_hash(user.password, password):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('adminPanel'))
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("logout.html")


@app.route('/blog')
def blogArchive():
    posts = parsePostQuery(Post.query.order_by(Post.id.desc()).all())
    return render_template('blog_archive.html',
                           posts=posts)


@app.route('/admin')
@login_required
def adminPanel():
    posts = []
    for post in Post.query.order_by(Post.id.desc()).all():
        posts.append({
            'id': post.id,
            'title': post.title,
            'status': post.status,
            'date': parseDate(post.date),
            'num_comments': len(post.comments),
            'url_path': post.url_path})
    return render_template('admin_page.html',
                           posts=posts)


@app.route('/editor')
@app.route('/editor/<post_id>')
@login_required
def postEditor(post_id=None):
    if not post_id:
        return render_template('post_editor.html',
                               post_id=post_id,
                               title='',
                               url_path='',
                               content='')
    else:
        entry = Post.query.filter(Post.id == post_id).first()
        return render_template('post_editor.html',
                               post_id=post_id,
                               title=entry.title,
                               url_path=entry.url_path,
                               content=entry.content)


@app.route('/submit', methods=['POST'])
def submitPost():
    post_id = request.form['post-id']
    title = request.form['post-title']
    url_path = request.form['url-path']
    content = request.form['post-content']
    entry = Post.query.filter(Post.id == post_id).first()
    if entry:
        entry.title = title
        entry.url_path = url_path
        entry.content = content
        entry.status = 'staged'
    else:
        p = Post(title=title,
                 url_path=url_path,
                 content=content)
        db.session.add(p)
    db.session.commit()
    return redirect(url_for('preview-post', post_path=url_path))


@app.route('/publish/<post_id>')
@login_required
def publishPost(post_id=None):
    entry = Post.query.filter(Post.id == post_id).first()
    entry.status = 'published'
    db.session.commit()
    return redirect(url_for('getBlogPost', post_path=entry.url_path))


@app.route('/post/<post_path>')
@app.route('/preview/<post_path>', endpoint='preview-post')
def getBlogPost(post_path=None):
    entry = Post.query.filter(Post.url_path == post_path).first()
    md_content = markdown.markdown(entry.content, ['codehilite'])
    post_id = entry.id
    if entry.status == 'staged':
        post_button = True
    else:
        post_button = False
    return render_template('blog_post.html',
                           post_id=post_id,
                           title=entry.title,
                           date=parseDate(entry.date),
                           content=md_content,
                           post_button=post_button)


@app.errorhandler(401)
def unauthorized(error):
    return render_template('login.html')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html')


@app.errorhandler(500)
def internalServiceError(error):
    return render_template('500.html')
