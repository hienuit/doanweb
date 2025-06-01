# seed.py
from app import create_app, db
from app.models.destinations import Destinations, seed_destinations
from sqlalchemy.sql import text

app = create_app()

with app.app_context():
    Destinations.query.delete()
    db.session.commit()
    db.session.execute(text("ALTER SEQUENCE destinations_id_seq RESTART WITH 1"))

    seed_destinations()
