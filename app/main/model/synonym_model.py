from app.main import db


class Synonym(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    synonym = db.Column(db.String(255), unique=True, nullable=False)
    snapshots = db.relationship("Snapshot", back_populates="synonym")
