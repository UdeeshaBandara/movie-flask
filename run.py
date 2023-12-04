from app import app
from app.routes import configure_routes

configure_routes()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=0)

