from flask import Flask

app = Flask(__name__)

from website import views, models
