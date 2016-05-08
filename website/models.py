from website import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), index=True)
    content = db.Column(db.Text)
    status = db.Column(db.String(255), default='staged')
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    url_path = db.Column(db.String(255))
