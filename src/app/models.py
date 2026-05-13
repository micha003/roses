from . import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")


class Rose(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.ForeignKey("user.id"), nullable=False)
    sender_name = db.Column(db.ForeignKey("user.name"), nullable=True)
    recipient_email = db.Column(db.String(80), nullable=False)
    recipient_name = db.Column(db.String(80), nullable=True)
    message = db.Column(db.String(200), nullable=True)

    sent_at = db.Column(db.DateTime, server_default=db.func.now())
