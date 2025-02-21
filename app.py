
from flask import Flask
from routes import register_routes

app = Flask(__name__)
app.config.from_object('config.Config')

register_routes(app)
