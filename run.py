from app import app
from app.routes import configure_routes

configure_routes()

if __name__ == '__main__':
    app.run(debug=True)

