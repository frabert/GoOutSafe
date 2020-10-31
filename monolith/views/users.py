from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required, logout_user, current_user, login_user
from sqlalchemy.orm import aliased

from monolith.auth import admin_required, is_admin, operator_required, health_authority_required
from monolith.forms import UserForm, OperatorForm, LoginForm
from monolith.database import User, db, Restaurant, Booking
from datetime import timedelta, datetime

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    if is_admin():
        users = db.session.query(User)
        return render_template("users.html", users=users)

def get_user_contacts(user_id, date_begin, date_end):
    SimultaneousBooking = aliased(Booking)
    contacts = db.session.query(User).\
            join(Booking, Booking.user_id == User.id).\
            filter(Booking.booking_datetime >= date_begin).\
            filter(Booking.booking_datetime < date_end).\
            join(Restaurant, Restaurant.id == Booking.rest_id).\
            join(SimultaneousBooking,
                SimultaneousBooking.user_id == user_id and \
                Booking.rest_id == SimultaneousBooking.rest_id and \
                Booking.booking_datetime.year == SimultaneousBooking.booking_datetime.year and \
                Booking.booking_datetime.month == SimultaneousBooking.booking_datetime.month and \
                Booking.booking_datetime.day == SimultaneousBooking.booking_datetime.day).\
            filter(User.id != user_id).\
            all()
    return contacts

@users.route('/users/<int:user_id>/contacts')
@health_authority_required
def user_contacts(user_id):
    return render_template("users.html",
        users=get_user_contacts(user_id, datetime.today() - timedelta(days=14), datetime.today()))


@users.route('/bookings', methods=['GET', 'POST'])
@login_required
def user_bookings():
    if current_user.is_admin or current_user.is_health_authority or current_user.rest_id is not None:
        return make_response(render_template('error.html', error='404'),404)

    now = datetime.now()

    qry = db.session.query(Booking,Restaurant)\
                    .filter(Booking.rest_id == Restaurant.id)\
                    .filter(Booking.user_id == current_user.id)\
                    .filter(Booking.booking_datetime >= now)\
                    .order_by(Booking.booking_datetime).all()
    
    if qry == []:
        flash("There are no reservations", "warning")

    return make_response(render_template('bookings.html', bookings=qry, title="Your Bookings"),200)

@users.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_user():
    if current_user.is_admin or current_user.is_health_authority:
        return make_response(render_template('error.html', error='401'),401)
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email, password = form.data['email'], form.data['password']
            q = db.session.query(User).filter(User.email == email)
            user = q.first()
            if user is not None and user.authenticate(password) and current_user.id == user.id:
                if current_user.is_positive:
                    flash('You cannot delete your data as long as you are positive','error')
                else:
                    q_r = db.session.query(Restaurant).filter_by(id = user.rest_id)	
                    rest = q_r.first()
                    logout_user()
                    db.session.delete(user)
                    if rest is not None:	
                        db.session.delete(rest)
                    db.session.commit()
                    flash('Your account has been deleted','success')
                return redirect('/', code=302)
            flash('Wrong email or password','error')
            return make_response(render_template('form.html', form=form, title="Unregister"),400)
        flash('Bad form','error')
        return make_response(render_template('form.html', form=form, title="Unregister"),400)
    return make_response(render_template('form.html', form=form, title="Unregister"),200)

@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Sign in!"),200)

            userGetMail = User.query.filter_by(email=form.email.data).first()
            userGetPhone = User.query.filter_by(phone=form.telephone.data).first()
            userGetSSN = None

            if form.ssn.data is not None and form.ssn.data != "":
                userGetSSN = User.query.filter_by(ssn=form.ssn.data).first()
            else:
                form.ssn.data = None

            if userGetMail is None and userGetPhone is None and userGetSSN is None:
                new_user = User()
                new_user.firstname = form.firstname.data
                new_user.lastname = form.lastname.data
                new_user.email = form.email.data
                new_user.set_password(form.password.data)
                new_user.phone = form.telephone.data
                new_user.dateofbirth = form.dateofbirth.data
                new_user.ssn = form.ssn.data
                try:
                    new_user.set_password(form.password.data)  # pw should be hashed with some salt
                    db.session.add(new_user)
                    db.session.commit()
                except: # Remove if coverage < 90%
                    flash('User not inserted','error')
                    return make_response(render_template('form.html', form=form, title="Sign in!"),500)
            else:
                flash('Existing user', 'error')
                return make_response(render_template('form.html', form=form, title="Sign in!"),400)

            if new_user is not None and new_user.authenticate(password):
                login_user(new_user)
            flash('User registerd succesfully', 'success')
            return redirect("/")

    return render_template('form.html', form=form, title="Sign in!")


@users.route('/create_operator', methods=['GET', 'POST'])
def create_operator():
    form = OperatorForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Sign in!"),200)

            userRestaurant = Restaurant.query.filter_by(name=form.restaurant_name.data).first()

            userGetMail = User.query.filter_by(email=form.email.data).first()
            userGetPhone = User.query.filter_by(phone=form.telephone.data).first()

            if userRestaurant is None:
                new_rest = Restaurant()
                new_rest.name = form.restaurant_name.data
                new_rest.lat = form.restaurant_latitude.data
                new_rest.lon = form.restaurant_longitude.data
                new_rest.phone = form.restaurant_phone.data
                if userGetMail is None and userGetPhone is None:
                    new_user = User()
                    new_user.firstname = form.firstname.data
                    new_user.lastname = form.lastname.data
                    new_user.email = form.email.data
                    new_user.set_password(form.password.data)
                    new_user.phone = form.telephone.data
                    new_user.dateofbirth = form.dateofbirth.data
                    try:
                        # pw should be hashed with some salt
                        db.session.add(new_rest)
                        db.session.commit()
                        new_user.rest_id = new_rest.id
                        db.session.add(new_user)
                        db.session.commit()

                    except: # Remove if coverage < 90%
                        flash('New operator and Restaurant not inserted','error')
                        return make_response(render_template('form.html', form=form, title="Sign in!"),500)
                else:
                    flash('Existing operator', 'error')
                    return make_response(render_template('form.html', form=form, title="Sign in!"), 400)
            else:
                flash('Existing restaurant', 'error')
                return make_response(render_template('form.html', form=form, title="Sign in!"), 400)

            if new_user is not None and new_user.authenticate(password):
                login_user(new_user)
            flash('Restaurant registerd succesfully', 'success')
            return redirect("/")

    return render_template('form.html', form=form, title="Sign in!")

