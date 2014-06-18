from flask import Flask

def create_app(config_name):
    app = Flask(__name__)

    from api_0_1 import api as api_0_1_blueprint
    app.register_blueprint(api_0_1_blueprint, url_prefix='/api/0.1')

    return app


if __name__ == '__main__':
    app = create_app(1)
    app.run(debug=True)
