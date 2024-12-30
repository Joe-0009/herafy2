from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user_count = User.query.count()
    print(f"Total users in database: {user_count}")

    # Optionally print details of the first few users
    users = User.query.limit(10).all()
    for user in users:
        print(f"User: {user.username}, Email: {user.email}, First Name: {user.first_name}, Last Name: {user.last_name}")
