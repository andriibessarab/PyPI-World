from extensions import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column("fullname", db.Text, nullable=False, unique=False)
    username = db.Column("username", db.Text, nullable=False, unique=True)
    email = db.Column("email", db.Text, nullable=False, unique=True)
    password = db.Column("password", db.Text, nullable=False, unique=False)
    pypi_token = db.Column("pypi_token", db.Text, nullable=True, unique=True)
    github_username = db.Column("github_username", db.Text, nullable=True, unique=False)
    github_token = db.Column("github_token", db.Text, nullable=True, unique=True)
    joined_on = db.Column("joined_on", db.DateTime, nullable=False, default=db.func.now())

    def to_json(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "pypi_token": self.pypi_token,
            "github_username": self.github_username,
            "github_token": self.github_token,
        }

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Package(db.Model):

    __tablename__ = "packages"

    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("users.id"), nullable=False)
    setup_id = db.Column("setup_id", db.Integer, db.ForeignKey("setups.id"), unique=True, nullable=True)
    pkg_name = db.Column("pkg_name", db.Text, nullable=False, unique=False)
    github_repo_name = db.Column("github_repo_name", db.Text, nullable=True, unique=True)
    is_published = db.Column("is_published", db.Boolean, nullable=False, default=False)
    updated_on = db.Column("updated_on", db.DateTime, nullable=True)
    created_on = db.Column("created_on", db.DateTime, nullable=False, default=db.func.now())


class Setup(db.Model):

    __tablename__ = "setups"

    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    name = db.Column("name", db.Text, nullable=False)
    version = db.Column("version", db.Text, nullable=False)
    description = db.Column("description", db.Text, nullable=True)
    long_description = db.Column("long_description", db.Text, nullable=True)
    author = db.Column("author", db.Text, db.ForeignKey("users.fullname"), nullable=False)
    author_email = db.Column("author_email", db.Text, db.ForeignKey("users.email"), nullable=False)
    keywords = db.Column("keywords", db.Text, nullable=True)
    python_version = db.Column("python_version", db.Integer, nullable=False)
