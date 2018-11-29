from app.main import db


class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spans_from = db.Column(db.DateTime, nullable=False)
    spans_to = db.Column(db.DateTime, nullable=False)
    keywords = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.Float, nullable=False)
    synonym = db.Column(db.String(255), nullable=False)
