from flask import Flask
from config import Config
from models import db, Admin
from flask_login import LoginManager
from routes import main
from flask_cors import CORS

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)
app.config.from_object(Config)

db.init_app(app)

CORS(app, supports_credentials=True)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

app.register_blueprint(main)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)