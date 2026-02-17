from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Import inside factory to avoid circular imports
    from marketmind_flask.routes.trade import trade_bp
    from marketmind_flask.routes.analyze import analyze_bp
    from marketmind_flask.routes.health import health_bp
    from marketmind_flask.routes.metrics import metrics_bp

    app.register_blueprint(trade_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(metrics_bp)

    return app