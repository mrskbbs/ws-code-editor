from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from app.config import BACKEND_DOMAIN_NAME, BACKEND_PORT, FLASK_SECERT_KEY, FRONTEND_URL
from app.models.base import Base
from app.routes.auth import router as auth_router
from app.ws.routes.room import RoomWSRoutes
from app.db import engine

# Flask HTTP app config
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY=FLASK_SECERT_KEY,
)
# TODO: improve resources security
CORS(app, supports_credentials=True)
app.register_blueprint(auth_router)

# Flask SocketIO config
socketio = SocketIO(
    app, 
    path="/ws",
    cors_allowed_origins=FRONTEND_URL, 
    cors_credentials=True,
    logger=True
)
socketio.init_app(app)
socketio.on_namespace(RoomWSRoutes("/ws/room", ))
Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(
        BACKEND_DOMAIN_NAME,
        BACKEND_PORT,
        debug=True
    )
    socketio.run(app)
    