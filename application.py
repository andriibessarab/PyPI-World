from flask import Flask
from extensions import db


def create_app(config_file="settings.py", jinja_globals="variables.py"):
    app = Flask("__name__")

    app.config.from_pyfile(config_file)

    from variables import inputs_info, setup_args_info
    import json
    app.jinja_env.globals["inputs_info"] = inputs_info
    app.jinja_env.globals["setup_args_info"] = setup_args_info
    app.jinja_env.filters["to_json"] = json.dumps

    from extensions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)

    from views.main import main
    from views.auth import auth
    from views.pkg import pkg
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(pkg)

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
