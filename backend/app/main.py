from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from app.routes.auth import router as auth_router
from app.routes.rooms import RoomWS

# Flask HTTP app config
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='secret',
)
CORS(app, resource={r"/*": "http://localhost:3000"})
app.register_blueprint(auth_router)

# Flask SocketIO config
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="http://localhost:3000")
socketio.on_namespace(RoomWS("/room"))

if __name__ == '__main__':
    app.run(
        "localhost",
        5000,
        debug=True
    )

    socketio.run(app)
    