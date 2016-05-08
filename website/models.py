from website import db


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), index=True)
    content = db.Column(db.Text)
    status = db.Column(db.String(255), default='staged')
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    url_path = db.Column(db.String(255))

    comments = db.relationship('Comment',
                               backref=db.backref('post', lazy='joined'))


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    name = db.Column(db.String(255))
    comment = db.Column(db.Text)


class User(db.Model):
    __tablename__ = 'user'

    email = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255))
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
