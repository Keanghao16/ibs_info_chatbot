from src.web.app import create_app
from src.web.websocket_manager import socketio

if __name__ == "__main__":
    app = create_app()
    # Use socketio.run instead of app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)