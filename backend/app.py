from flask import Flask
from flask_cors import CORS
from routes.plans import plans_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(plans_bp, url_prefix='/api')

@app.route('/')
def index():
    return "Welcome to the RoboCasa Plan API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)