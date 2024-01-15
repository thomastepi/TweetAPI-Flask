from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from flask_swagger_ui import get_swaggerui_blueprint
from blueprints.basic_endpoints import blueprint as basic_endpoints

app = Flask(__name__)
CORS(app)
app.register_blueprint(basic_endpoints)


SWAGGER_URL = '/swagger'
API_URL = 'http://127.0.0.1:5000/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sample API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))


if __name__ == '__main__':
    app.run(debug=True)
