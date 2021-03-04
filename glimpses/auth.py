from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_user

from glimpses import app, login_manager
from glimpses.model import User


@app.route('/pass', methods=['GET', 'POST'])
def _pass():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.get(1)
        if user and user.check_password(password=password):
            login_user(user)
            return redirect(url_for('home'))
        return redirect(url_for('_pass'))

    return render_template('pass.html')


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    return redirect(url_for('_pass'))
