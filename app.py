from flask import Flask
from routes import register_routes
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')

@app.template_filter('datetimefilter')
def datetime_filter(value, format='%Y'):
    return datetime.now().strftime(format)

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)