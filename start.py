from app import app, db
from app.models import User, Oprecord, OwnerPost


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Oprecord': Oprecord, 'OwnerPost': OwnerPost, 'Booking': Booking}