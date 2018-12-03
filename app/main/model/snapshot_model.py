from app.main import db


class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spans_from = db.Column(db.DateTime, nullable=False)
    spans_to = db.Column(db.DateTime, nullable=False)
    statistics = db.Column(db.JSON, nullable=False)
    sentiment = db.Column(db.Float, nullable=False)
    synonym_id = db.Column(db.Integer, db.ForeignKey('synonym.id'), primary_key=True)
