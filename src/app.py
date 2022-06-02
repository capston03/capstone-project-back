from flask import Flask
from blueprints.blueprints import blueprint_user, \
    blueprint_image, blueprint_beacon, blueprint_building, blueprint_episode

app = Flask(__name__)
app.register_blueprint(blueprint_user)
app.register_blueprint(blueprint_beacon)
app.register_blueprint(blueprint_building)
app.register_blueprint(blueprint_image)
app.register_blueprint(blueprint_episode)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
