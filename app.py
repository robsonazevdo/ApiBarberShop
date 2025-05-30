from flask import Flask
from flask_cors import CORS
from auth import auth
from barbers import barbers
from barbers import barber
from appointments import appointments
from database import get_db, close_connection





app = Flask(__name__)

# Libera tudo (para teste). Depois você pode restringir.
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.register_blueprint(auth)
app.register_blueprint(barbers)
app.register_blueprint(barber)
app.register_blueprint(appointments)
app.teardown_appcontext(close_connection)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
