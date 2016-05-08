import markdown
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from website import app, db
from website.models import Post
from flask import render_template, request, url_for, redirect


def parseDate(sql_date):
    date_object = datetime.strptime(sql_date.split(' ')[0], '%Y-%m-%d')
    return date_object.strftime('%B %d, %Y')


@app.route('/')
def index():
    three_posts = Post.query.filter(
        Post.status == 'published').order_by(Post.id.desc()).limit(3)
    recent_posts = []
    for post in three_posts:
        html = markdown.markdown(post.content)
        html_text = BeautifulSoup(html).findAll(text=True)
        text_preview = ''.join(html_text)[:100] + '...'
        recent_posts.append({'title': post.title,
                             'preview': text_preview,
                             'date': parseDate(str(post.date)),
                             'url_path': post.url_path})
    return render_template('home_page.html',
                           recent_posts=recent_posts)


@app.route('/editor')
def postEditor():
    return render_template('post_editor.html')


@app.route('/submit', methods=['POST'])
def submitPost():
    title = request.form['post-title']
    url_path = request.form['url-path']
    content = request.form['post-content']
    p = Post(title=title,
             url_path=url_path,
             content=content)
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('preview-post', post_path=url_path))


@app.route('/publish/<post_id>')
def publishPost(post_id=None):
    entry = Post.query.filter(Post.id == post_id).first()
    entry.status = 'published'
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/<post_path>')
@app.route('/preview/<post_path>', endpoint='preview-post')
def getBlogPost(post_path=None):
    entry = Post.query.filter(Post.url_path == post_path).first()
    if not entry:
        return render_template('404.html')
    md_content = markdown.markdown(entry.content, ['codehilite'])
    post_id = entry.id
    if entry.status == 'staged':
        post_button = True
    else:
        post_button = False
    return render_template('blog_post.html',
                           post_id=post_id,
                           title=entry.title,
                           date=entry.date,
                           content=md_content,
                           post_button=post_button)
