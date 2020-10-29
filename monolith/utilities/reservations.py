from monolith.database import db, Restaurant, Like, Booking, User, Table
from monolith.auth import current_user
from datetime import timedelta

def book_a_table(restaurant, number_of_person, booking_datetime, table):
    new_booking = Booking()
    new_booking.user_id = current_user.id
    new_booking.rest_id = restaurant.id
    new_booking.person_number = number_of_person
    new_booking.booking_datetime = booking_datetime
    new_booking.table_id = table
    db.session.add(new_booking)
    db.session.commit()

def get_table(restaurant, number_of_people, booking_datetime):
    delta = restaurant.occupation_time
    starting_period = booking_datetime - timedelta(hours=delta)
    ending_period = booking_datetime + timedelta(hours=delta)
    occupied = db.session.query(Table.id).select_from(Booking,Table)\
                        .filter(Booking.table_id == Table.id)\
                        .filter(Booking.rest_id == restaurant.id)\
                        .filter(starting_period < Booking.booking_datetime)\
                        .filter(Booking.booking_datetime < ending_period )\
                        .all() #GB < or <= ? Better <

    total = db.session.query(Table.id,Table.capacity).select_from(Table,Restaurant)\
                        .filter(Restaurant.id == Table.rest_id)\
                        .all()

    free_tables = [t for t in total if ( ( (t[0],) not in occupied) and (t[1] >= number_of_people) )] # returns the free table usable by this number of people
    free_tables.sort(key=lambda x:x[1]) # order the tables from the smaller

    if free_tables == []:
        return None
    return free_tables[0][0] # return the smaller table that can be used


def try_to_book(restaurant_id, number_of_people, booking_datetime):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).all()[0]
    if record.is_open(booking_datetime):
        table = get_table(record, number_of_people, booking_datetime)
        if table is not None:
            book_a_table(record, number_of_people, booking_datetime, table)
            return True
    return False