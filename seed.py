from faker import Faker
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

fake = Faker()
app = create_app()

def create_fake_user():
    password_hash = generate_password_hash('password', method='pbkdf2:sha256')
    return User(
        email=fake.email(),
        username=fake.user_name(),
        password=password_hash,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        location=fake.city(),
        profession=fake.job(),
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
        about_me=fake.text(max_nb_chars=200)
    )

with app.app_context():
    db.create_all()
    users = [create_fake_user() for _ in range(10000)]
    db.session.bulk_save_objects(users)
    db.session.commit()
    print("50 users have been added to the database.")

    # Verification
    user_count = User.query.count()
    print(f"Total users in database: {user_count}")

    # Optionally print details of the first few users
    users = User.query.limit(10).all()
    for user in users:
        print(f"User: {user.username}, Email: {user.email}, First Name: {user.first_name}, Last Name: {user.last_name}")
