import os
import click
from flask import url_for

from app import create_app, db
from app.models import User, Level

# optional import for freezing the site; wrapped in try/except so the CLI still works without it
try:
    from flask_frozen import Freezer
except ImportError:
    Freezer = None

app = create_app(os.getenv('FLASK_ENV') or 'development')

@app.cli.command()
@click.option('--username', prompt=True)
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin(username, email, password):
    """Create an admin user."""
    if User.query.filter((User.username == username) | (User.email == email)).first():
        click.echo(f'Error: A user with username "{username}" or email "{email}" already exists.', err=True)
        return
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Admin user {username} created successfully!')

@app.cli.command()
def seed_levels():
    """Seed initial game levels."""
    levels = [
        {'name': 'Level 1 - Tutorial', 'description': 'Learn the basics', 'difficulty': 'Easy'},
        {'name': 'Level 2 - Getting Started', 'description': 'Apply your skills', 'difficulty': 'Easy'},
        {'name': 'Level 3 - Intermediate Challenge', 'description': 'Test your abilities', 'difficulty': 'Medium'},
        {'name': 'Level 4 - Advanced Tactics', 'description': 'Master complex mechanics', 'difficulty': 'Medium'},
        {'name': 'Level 5 - Expert Trial', 'description': 'Push your limits', 'difficulty': 'Hard'},
        {'name': 'Level 6 - Nightmare Mode', 'description': 'Only for the best', 'difficulty': 'Hard'},
    ]
    for level_data in levels:
        existing = Level.query.filter_by(name=level_data['name']).first()
        if not existing:
            level = Level(**level_data)
            db.session.add(level)
    db.session.commit()
    click.echo('Levels seeded successfully!')

@app.cli.command()
def list_users():
    """List all registered users."""
    users = User.query.all()
    if not users:
        click.echo('No users found.')
        return
    for user in users:
        role = 'Admin' if user.is_admin else 'User'
        click.echo(f'ID: {user.id} | Username: {user.username} | Email: {user.email} | Role: {role}')
        click.echo(f'ID: {user.id} | Username: {user.username} | Email: {user.email} | Role: {role} | Password Hash: {user.password}')

@app.cli.command()
@click.argument('username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def reset_password(username, password):
    """Reset a user's password."""
    user = User.query.filter_by(username=username).first()
    if not user:
        click.echo(f'Error: User "{username}" not found.', err=True)
        return
    user.set_password(password)
    db.session.commit()
    click.echo(f'Password for "{username}" has been updated successfully.')
@app.cli.command()
def freeze():
    """Generate a static version of the site (requires Flask-Frozen).

    The generated files will be placed in a folder called `build/` by default.
    You can then push that directory to a GitHub Pages branch or serve it
    however you like.  Only the routes below are included; interactive
    features (login, form submissions, database mutations) won’t work in
    the snapshot.

    A couple of details to keep in mind:
    * `FREEZER_BASE_URL` may need to be set to the repo path if you're
      deploying to a project page (e.g.
      https://username.github.io/repo-name/).
    * If the database isn't accessible (e.g. on a fresh machine without
      PostgreSQL) the command will still produce the homepage/leaderboard
      but user profiles will be skipped.
    """
    if Freezer is None:
        click.echo('The Frozen-Flask package is not installed. Install it with `pip install Frozen-Flask`.', err=True)
        return

    # allow override of base URL for project pages
    base = os.environ.get('FREEZER_BASE_URL')
    if base:
        app.config['FREEZER_BASE_URL'] = base

    # by default Frozen-Flask writes into app.root_path/build; override it so
    # the static files appear at the repository root (where GitHub Actions
    # expects them).
    project_root = os.path.abspath(os.path.join(app.root_path, os.pardir))
    app.config['FREEZER_DESTINATION'] = os.path.join(project_root, 'build')

    # ensure database exists and has some data for freezing
    try:
        with app.app_context():
            db.create_all()
            # seed default levels if none exist
            if Level.query.count() == 0:
                for lvl in [
                    {'name': 'Level 1 - Tutorial', 'description': 'Learn the basics', 'difficulty': 'Easy'},
                    {'name': 'Level 2 - Getting Started', 'description': 'Apply your skills', 'difficulty': 'Easy'},
                    {'name': 'Level 3 - Intermediate Challenge', 'description': 'Test your abilities', 'difficulty': 'Medium'},
                    {'name': 'Level 4 - Advanced Tactics', 'description': 'Master complex mechanics', 'difficulty': 'Medium'},
                    {'name': 'Level 5 - Expert Trial', 'description': 'Push your limits', 'difficulty': 'Hard'},
                    {'name': 'Level 6 - Nightmare Mode', 'description': 'Only for the best', 'difficulty': 'Hard'},
                ]:
                    db.session.add(Level(**lvl))
                db.session.commit()
    except Exception:
        pass

    freezer = Freezer(app)

    # generate all user profile pages so links don't 404 (ignore DB errors)
    @freezer.register_generator
    def user_profile():
        try:
            users = User.query.all()
        except Exception:
            users = []
        for user in users:
            yield 'users.profile', {'username': user.username}

    # other simple routes could be added explicitly if needed,
    # but "freezer.freeze()" will automatically visit the static
    # endpoints such as `/` and `/leaderboard`.

    freezer.freeze()
    click.echo('Static site generated in the `build/` directory.')

if __name__ == '__main__':
    # Ensure database tables exist and seed levels if needed
    with app.app_context():
        db.create_all()
        if Level.query.count() == 0:
            default_levels = [
                {'name': 'Level 1 - Tutorial', 'description': 'Learn the basics', 'difficulty': 'Easy'},
                {'name': 'Level 2 - Getting Started', 'description': 'Apply your skills', 'difficulty': 'Easy'},
                {'name': 'Level 3 - Intermediate Challenge', 'description': 'Test your abilities', 'difficulty': 'Medium'},
                {'name': 'Level 4 - Advanced Tactics', 'description': 'Master complex mechanics', 'difficulty': 'Medium'},
                {'name': 'Level 5 - Expert Trial', 'description': 'Push your limits', 'difficulty': 'Hard'},
                {'name': 'Level 6 - Nightmare Mode', 'description': 'Only for the best', 'difficulty': 'Hard'},
            ]
            for lvl in default_levels:
                level = Level(**lvl)
                db.session.add(level)
            db.session.commit()
    app.run()
