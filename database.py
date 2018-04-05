#!/usr/bin/env python3

from modules import pg8000
import configparser
import json
import time
import datetime

#####################################################
##  Database Connect
#####################################################

'''
Connects to the database using the connection string
'''
def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        # Parses the config file and connects using the connect string
        connection = pg8000.connect(database=config['DATABASE']['user'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.InterfaceError as e:
        print("Interface error")
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    # return the connection to use
    return connection

#####################################################
##  Login
#####################################################

'''
Check that the users information exists in the database.

- True = return the user data
- False = return None
'''
def check_login(member_id, password):

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                    FROM v1
                 WHERE member_id=%s AND pass_word=%s"""
        print('hello')
        cur.execute(sql, (member_id, password))
        print('hello2')
        user_data = cur.fetchone()              # Fetch the first row
        print('hello3')
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if user_data is None:
        return None

    # TODO
    # Check if the user details are correct!
    # Return the relevant information (watch the order!)

    # TODO Dummy data - change rows to be useful!
    # FORMAT = [member_id, title, firstname, familyname, countryName, residence]
    # user_data = ['1141171337', 'Mr', 'Potato', 'Head', 'Australia', 'SIT']
    # Get the member's type
    # user_type = ['official']

    print(user_data)
    
    try:
        sql = """SELECT COUNT(1)
                    FROM v2
                 WHERE member_id=%s"""
        cur.execute(sql, (user_data[0],))
        returned = cur.fetchone()
        print(returned)
        if returned[0] == 1:
            user_type = ['athlete']
        elif returned[0] == 0:
            sql = """SELECT COUNT(1)
                    FROM v3
                 WHERE member_id=%s"""
            cur.execute(sql, (user_data[0],))
            returned = cur.fetchone()
            print(returned)
            if returned[0] == 1:
                user_type = ['official']
            elif returned[0] == 0:
                sql = """SELECT COUNT(1)
                            FROM v4
                          WHERE member_id=%s"""
                cur.execute(sql, (user_data[0],))
                returned = cur.fetchone()
                print(returned)
                if returned[0] == 1:
                    user_type = ['staff']
                else:
                    return None
            else:
                return None
        else:
            return None
    except:
        return None

    try:
        tuples = {
                'member_id': user_data[0],
                'title': user_data[1],
                'first_name': user_data[2],
                'family_name': user_data[3],
                'country_name': user_data[4],
                'residence': user_data[5],
                'member_type': user_type[0]
            }
    except:
        return None
    return tuples



#####################################################
## Member Information
#####################################################

def member_details(member_id, mem_type):

    # TODO
    # Return all of the user details including subclass-specific details
    #   e.g. events participated, results.

    # TODO - Dummy Data (Try to keep the same format)
    # Accommodation [name, address, gps_lat, gps_long]
    accom_rows = ['SIT', '123 Some Street, Boulevard', '-33.887946', '151.192958']

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

    member_information_db = [None]*5

    # Check what type of member we are
    if(mem_type == 'athlete'):
        try:
            # Total medals
            sql = """SELECT COUNT(*)
                        FROM participates
                     WHERE athlete_id=%s"""
            cur.execute(sql, (member_id,))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[0] = returned[0]
            else:
                member_information_db[0] = None

            # Gold medals
            sql = """SELECT COUNT(*)
                     FROM participates
                     WHERE athlete_id=%s AND medal=%s;"""
            cur.execute(sql, (member_id,'G'))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[1] = returned[0]
            else:
                member_information_db[1] = None

            # Silver medals
            cur.execute(sql, (member_id, 'S'))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[2] = returned[0]
            else:
                member_information_db[2] = None

            # Bronze medals
            cur.execute(sql, (member_id, 'B'))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[3] = returned[0]
            else:
                member_information_db[3] = None

            # Number of bookings
            sql = """SELECT COUNT(*)
                     FROM booking
                     WHERE booked_for=%s"""
            cur.execute(sql, (member_id,))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[4] = returned[0]
            else:
                member_information_db[4] = None


        except:
            return None

        # TODO get the details for athletes
        # Member details [total events, total gold, total silver, total bronze, number of bookings]
        # member_information_db = [5, 2, 1, 2, 20]

        for i in range(0, len(member_information_db)):
            if (member_information_db[i]== None):
                member_information_db[i] = ''

        member_information = {
            'total_events': member_information_db[0],
            'gold': member_information_db[1],
            'silver': member_information_db[2],
            'bronze': member_information_db[3],
            'bookings': member_information_db[4]
        }


    elif(mem_type == 'official'):

        # TODO get the relevant information for an official
        # Official = [ Role with greatest count, total event count, number of bookings]
        # member_information_db = ['Judge', 10, 20]

        try:

            # Favourite role
            sql = """SELECT role, COUNT(member_id)
                     FROM runsevent
                     WHERE member_id=%s
                     GROUP BY role, member_id
                     ORDER BY COUNT(member_id) DESC"""
            cur.execute(sql, (member_id,))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[0] = returned[0]
            else:
                member_information_db[0] = None

            # Total events
            sql = """SELECT COUNT(*)
                     FROM runsevent
                     WHERE member_id=%s"""
            cur.execute(sql, (member_id,))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[1] = returned[0]
            else:
                member_information_db[1] = None

            # Total bookings
            sql = """SELECT COUNT(*)
                     FROM booking
                     WHERE booked_for=%s OR booked_by=%s"""
            cur.execute(sql, (member_id, member_id))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[2] = returned[0]
            else:
                member_information_db[2] = None

        except:
            return None

        for i in range(0, len(member_information_db)):
            if (member_information_db[i]== None):
                member_information_db[i] = ''

        member_information = {
            'favourite_role' : member_information_db[0],
            'total_events' : member_information_db[1],
            'bookings': member_information_db[2]
        }
    else:

        # TODO get information for staff member
        # Staff = [number of bookings ]
        # member_information_db = [10]

        try:
            sql = """SELECT COUNT(*)
                     FROM booking
                     WHERE booked_for=%s OR booked_by=%s"""
            cur.execute(sql, (member_id, member_id))
            returned = cur.fetchone()
            if (returned != None):
                member_information_db[0] = returned[0]
            else:
                member_information_db[0] = None
        except:
            return None

        for i in range(0, len(member_information_db)):
            if (member_information_db[i]== None):
                member_information_db[i] = ''

        member_information = {'bookings': member_information_db[0]}

    try:
        sql = """SELECT  *
                    FROM v5
                 WHERE member_id = %s"""
        cur.execute(sql, (member_id,))
        accom_rows = cur.fetchone()
    except:
        return None

    for i in range(0, len(accom_rows)):
            if (accom_rows[i]== None):
                accom_rows[i] = ''

    accommodation_details = {
        'name': accom_rows[0],
        'address': accom_rows[1],
        'gps_lat': accom_rows[2],
        'gps_lon': accom_rows[3]
    }

    # Leave the return, this is being handled for marking/frontend.
    return {'accommodation': accommodation_details, 'member_details': member_information}
#####################################################
##  Booking (make, get all, get details)
#####################################################

'''
Make a booking for a member.
Only a staff type member should be able to do this ;)
Note: `my_member_id` = Staff ID (bookedby)
      `for_member` = member id that you are booking for
'''
def make_booking(my_member_id, for_member, vehicle, date, hour, start_destination, end_destination):

    # TODO - make a booking
    # Insert a new booking
    # Only a staff member should be able to do this!!
    # Make sure to check for:
    #       - If booking > capacity
    #       - Check the booking exists for that time/place from/to.
    #       - Update nbooked
    #       - Etc.
    # return False if booking was unsuccessful :)
    # We want to make sure we check this thoroughly
    # MUST BE A TRANSACTION ;)

    conn = database_connect()
    if (conn is None):
        return False
    cur = conn.cursor()

    lastID = -1

    if 1 == 1:
        # Try executing the SQL and get from the database
        sql = """SELECT * FROM v6;"""
        cur.execute(sql,)
        lastID = cur.fetchone()[0]
        lastID = lastID + 1

        if lastID == -1:
            return False

        if int(hour) < 10:
            timestamp = date + ' 0' + hour + ':00:00'
        else:
            timestamp = date + ' ' + hour + ':00:00'

        sql1 = """INSERT INTO journey VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        sql2 = """INSERT INTO booking VALUES (%s, %s, %s, %s);"""

        # "When you issue the first SQL statement to the PostgreSQL database using a cursor object,
        #  psycopg creates a new transaction. From that moment, psycopg executes all the subsequent
        #  statements in the same transaction. - http://www.postgresqltutorial.com/postgresql-python/transaction/

        cur.execute(sql1, (lastID, timestamp, start_destination, end_destination, vehicle, 1, timestamp))
        cur.execute(sql2, (for_member, my_member_id, datetime.datetime.now(), lastID))
        conn.commit()

    return True


'''
List all the bookings for a member
'''
def all_bookings(member_id):

    # TODO - fix up the bookings_db information
    # Get all the bookings for this member's ID
    # You might need to join a few things ;)
    # It will be a list of lists - e.g. your rows

    # Format:
    # [
    #    [ vehicle, startday, starttime, to, from ],
    #   ...
    # ]

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT * FROM v7
                 WHERE booked_for = %s;"""
        cur.execute(sql, (member_id,))
        bookings_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if bookings_db is None:
        bookings = [{
            'vehicle': None,
            'start_day': None,
            'start_time': None,
            'to': None,
            'from': None
        }]
        return bookings

    bookings = [{
        'vehicle': row[0],
        'start_day': row[1],
        'start_time': row[2],
        'to': row[3],
        'from': row[4]
    } for row in bookings_db]

    return bookings
'''
List all the bookings for a member on a certain day
'''
def day_bookings(member_id, day):

    # TODO - fix up the bookings_db information
    # Get bookings for the member id for just one day
    # You might need to join a few things ;)
    # It will be a list of lists - e.g. your rows

    # Format:
    # [
    #    [ vehicle, startday, starttime, to, from ],
    #   ...
    # ]

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                    FROM v7
                 WHERE booked_for = %s AND dt = %s;"""
        cur.execute(sql, (member_id, day))
        bookings_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if bookings_db is None:
        bookings = [{
            'vehicle': None,
            'start_day': None,
            'start_time': None,
            'to': None,
            'from': None
        }]
        return bookings

    bookings = [{
        'vehicle': row[0],
        'start_day': row[1],
        'start_time': row[2],
        'to': row[3],
        'from': row[4]
    } for row in bookings_db]

    return bookings
'''
Get the booking information for a specific booking
'''
def get_booking(b_date, b_hour, vehicle, from_place, to_place):

    # TODO - fix up the row to get booking information
    # Get the information about a certain booking, including who booked etc.
    # It will include more detailed information

    # Format:
    #   [vehicle, startday, starttime, to, from, booked_by (name of person), when booked]
    #row = ['TR870R', '21/12/2020', '0600', 'SIT', 'Wentworth', 'Mike', '21/12/2012']
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """SELECT vehicle_code, depart_time::date, depart_time::time,
                    P1.place_name, P2.place_name, given_names, EXTRACT(DAY FROM when_booked)
                    FROM (booking JOIN member ON booked_by = member_id) NATURAL JOIN (journey J JOIN place P1 ON J.to_place = P1.place_id JOIN place P2 on J.from_place = P2.place_id)
                    WHERE vehicle_code = %s AND J.to_place = %s AND J.from_place = %s
                        AND depart_time::date = %s AND depart_time::time = %s"""

        cur.execute(sql, (vehicle, to_place, from_place, b_date, b_hour))
        row = cur.fetchone();

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if row is None:

        booking = {
            'vehicle': None,
            'start_day': None,
            'start_time': None,
            'to': None,
            'from': None,
            'booked_by': None,
            'whenbooked': None
        }
        return booking


    booking = {
        'vehicle': row[0],
        'start_day': row[1],
        'start_time': row[2],
        'to': row[3],
        'from': row[4],
        'booked_by': row[5],
        'whenbooked': row[6]
    }

    return booking

#####################################################
## Journeys
#####################################################

'''
List all the journeys between two places.
'''
def all_journeys(from_place, to_place):

    # TODO - get a list of all journeys between two places!
    # List all the journeys between two locations.
    # Should be chronologically ordered
    # It is a list of lists

    # Format:
    # [
    #   [ vehicle, day, time, to, from, nbooked, vehicle_capacity],
    #   ...
    # ]
    #journeys_db = [
    #    ['TR470R', '21/12/2020', '0600', 'SIT', 'Wentworth', 7, 8]
    #]

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

    try:

        # Check if given name is a place or a location
        # If place:
            # Do the normal query
        # If location:
            # Do the recursive query

        sql = """SELECT vehicle_code, date(depart_time), TO_CHAR(EXTRACT(HOUR FROM depart_time), 'FM00') || TO_CHAR(EXTRACT(MINUTE FROM depart_time), 'FM00'), P1.place_name, P2.place_name, nbooked, capacity
                FROM (journey J JOIN place P1 ON J.to_place = P1.place_id JOIN place P2 on J.from_place = P2.place_id)
                    NATURAL JOIN vehicle
                    WHERE J.to_place = %s AND J.from_place = %s
                    ORDER BY depart_time
                    """

        sqlCheckLocation = """SELECT COUNT(1)
                           FROM location
                           WHERE name = %s"""
        cur.execute(sqlCheckLocation, (from_place,))
        fromLocationCheck = cur.fetchone()[0]
        cur.execute(sqlCheckLocation, (to_place,))
        toLocationCheck = cur.fetchone()[0]

        if (fromLocationCheck == 0 and toLocationCheck == 0):
            # Not Locations. Make sure they're places
            sqlCheckLocation = """SELECT COUNT(1)
                                  FROM place
                                  WHERE place_name = %s"""
            cur.execute(sqlCheckPlace, (from_place,))
            fromPlaceCheck = cur.fetchone()[0]
            cur.execute(sqlCheckPlace, (to_place,))
            toPlaceCheck = cur.fetchone()[0]
            if (fromPlaceCheck == 0 and toPlaceCheck == 0):
                # Not places or locations -> error
                return None
            elif (fromPlaceCheck == 0 and toPlaceCheck == 1) or (fromPlaceCheck == 1 and toPlaceCheck == 0):
                return None
            elif (fromPlaceCheck == 1 and toPlaceCheck == 1):
                # Both are places

                sqlPlaceID = """SELECT place_id
                                   FROM place
                                   WHERE place_name = %s"""
                cur.execute(sqlPlaceID, (from_place,))
                from_placeID = cur.fetchone()[0]
                cur.execute(sqlPlaceID, (to_place,))
                to_placeID = cur.fetchone()[0]

                cur.execute(sql, (to_placeID, from_placeID))
                journeys_db = cur.fetchall()


        elif (fromLocationCheck == 0 and toLocationCheck == 1) or (fromLocationCheck == 1 and toLocationCheck == 0):
            # One is a place the other is not -> error
            return None
        else:
            # Both are locations

            # Get the IDs of the given places for later use
            sqlLocationID = """SELECT location_id
                               FROM location
                               WHERE name = %s"""
            cur.execute(sqlLocationID, (from_place,))
            from_placeID = cur.fetchone()[0]
            cur.execute(sqlLocationID, (to_place,))
            to_placeID = cur.fetchone()[0]

            print(from_placeID)
            print(to_placeID)

            # Recursive query to get all locations that are children of given location
            sqlrecursive = """WITH RECURSIVE AllFrom (parent, child) AS (
                                    SELECT location_id, part_of
                                        FROM location
                                UNION
                                    SELECT parent, part_of
                                        FROM AllFrom
                                            JOIN location ON (child = location_id)
                            )
                            SELECT parent
                            FROM AllFrom
                            WHERE child = %s AND parent IS NOT NULL"""
            cur.execute(sqlrecursive, (from_placeID,))
            parentsArray = cur.fetchall()
            if parentsArray == None:
                parentsArray = ([from_placeID],)
            else:
                parentsArray = ([from_placeID],) + parentsArray
            cur.execute(sqlrecursive, (to_placeID,))
            childrenArray = cur.fetchall()
            if childrenArray == None:
                childrenArray = ([to_placeID],)
            else:
                childrenArray = ([to_placeID],) + childrenArray

            # At this point we have an array of all locations to run the sql query on
            # Get journeys for all places that are located in given locations
            getplacelocatedin = """SELECT vehicle_code, date(depart_time), TO_CHAR(EXTRACT(HOUR FROM depart_time), 'FM00') || TO_CHAR(EXTRACT(MINUTE FROM depart_time), 'FM00'), P1.place_name, P2.place_name, nbooked, capacity
                    FROM (journey J JOIN place P1 ON J.to_place = P1.place_id JOIN place P2 on J.from_place = P2.place_id) NATURAL JOIN vehicle
                    WHERE P2.located_in = %s and P1.located_in = %s"""

            journeys_db = ()
            print('hello1')
            print(len(parentsArray))
            print(len(childrenArray))
            # For every from_location and to_location, get journeys for all places that are located in them
            for i in range(0, len(parentsArray)):
                for j in range(0, len(childrenArray)):
                    cur.execute(getplacelocatedin, (parentsArray[i][0], childrenArray[j][0]))
                    print('hello')
                    journeys_db = journeys_db + cur.fetchall()
                    print(journeys_db)

    except:
          # If there were any errors, return a NULL row printing an error to the debug
        return None

    if journeys_db is None:
        #return None
        journeys = [{
            'vehicle': None,
            'start_day': None,
            'start_time': None,
            'to' : None,
            'from' : None
        }]
        return journeys

    journeys = [{
        'vehicle': row[0],
        'start_day': row[1],
        'start_time': row[2],
        'to' : row[3],
        'from' : row[4]
    } for row in journeys_db]

    return journeys


'''
Get all of the journeys for a given day, from and to a selected place.
'''
def get_day_journeys(from_place, to_place, journey_date):

    # TODO - update the journeys_db variable to get information from the database about this journey!
    # List all the journeys between two locations.
    # Should be chronologically ordered
    # It is a list of lists

    # Format:
    # [
    #   [ vehicle, day, time, to, from, nbooked, vehicle_capacity],
    #   ...
    # ]
    #journeys_db = [
    #    ['TR470R', '21/12/2020', '0600', 'SIT', 'Wentworth', 7, 8]
    #]
    #
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """SELECT vehicle_code, date(depart_time), TO_CHAR(EXTRACT(HOUR FROM depart_time), 'FM00') || TO_CHAR(EXTRACT(MINUTE FROM depart_time), 'FM00'), P1.place_name, P2.place_name, nbooked, capacity
                FROM (journey J JOIN place P1 ON J.to_place = P1.place_id JOIN place P2 on J.from_place = P2.place_id)
                        NATURAL JOIN vehicle
                WHERE J.to_place = %s AND J.from_place = %s AND date(depart_time) = %s
                ORDER BY depart_time"""

        cur.execute(sql, (to_place, from_place, journey_date))
        journeys_db = cur.fetchall()

    except:
          # If there were any errors, return a NULL row printing an error to the debug
        return None

    if journeys_db is None:
        #return None

        journeys = [{
            'vehicle': None,
            'start_day': None,
            'start_time': None,
            'to': None,
            'from': None
        }]
        return journeys

    journeys = [{
        'vehicle': row[0],
        'start_day': row[1],
        'start_time': row[2],
        'to': row[3],
        'from': row[4]
    } for row in journeys_db]


    return journeys


#####################################################
## Events
#####################################################

def all_events():

    # TODO - update the events_db to get all events
    # Get all the events that are running.
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # It is a list of lists
    # Chronologically order them by start

    # Format:
    # [
    #   [name, start, sport, venue_name]
    # ]

    # events_db = [
    #       ['200M Freestyle', '0800', 'Swimming', 'Olympic Swimming Pools'],
    #       ['1km Women\'s Cycle', '1800', 'Cycling', 'Velodrome']
    #   ]


    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT event_name, event_start, sport_name, place_name
                 FROM (Event NATURAL JOIN Sport) NATURAL JOIN (SportVenue NATURAL JOIN Place)
                 ORDER BY event_start ASC;"""
        cur.execute(sql)
        events_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if events_db is None:
        events = [{
            'name': None,
            'start': None,
            'sport': None,
            'venue': None,
        }]
        return events

    events = [{
        'name': row[0],
        'start': row[1],
        'sport': row[2],
        'venue': row[3],
    } for row in events_db]

    return events

currPage = '0'
currLimit = '0'
def all_events_filter(limit, page):

    # TODO - update the events_db to get all events
    # Get all the events that are running.
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # It is a list of lists
    # Chronologically order them by start

    # Format:
    # [
    #   [name, start, sport, venue_name]
    # ]

    # events_db = [
    #       ['200M Freestyle', '0800', 'Swimming', 'Olympic Swimming Pools'],
    #       ['1km Women\'s Cycle', '1800', 'Cycling', 'Velodrome']
    #   ]


    global currPage
    global currLimit

    if limit != '' and currLimit != limit:
        currLimit = limit

    if (page == 'next'):
        currPage = int(currPage) + 1
        currPage = str(currPage)
    elif page == 'prev':
        currPage = int(currPage) -1
        currPage = str(currPage)
    if int(currPage) < 0:
        currPage = 0
        currPage = str(currPage)

    begin = int(currPage) * int(currLimit)
    begin = str(begin)

    conn = database_connect()
    if (conn is None):
        print('Can\'t connect to database')
        return None
    cur = conn.cursor()
    try:
    # Try executing the SQL and get from the database
        sql = """SELECT event_name, event_start, sport_name, place_name
                FROM (Event NATURAL JOIN Sport) NATURAL JOIN (SportVenue NATURAL JOIN Place)
                ORDER BY event_start DESC
                LIMIT %s OFFSET %s;"""
        cur.execute(sql, (currLimit, begin,))
        events_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print('Can\'t fetch from database222')
        return None

    if events_db is None:
        return 0

    events = [{
        'name': row[0],
        'start': row[1],
        'sport': row[2],
        'venue': row[3],
    } for row in events_db]

    return events

'''
Get all the events for a certain sport - list it in order of start
'''
def all_events_sport(sportname):

    # TODO - update the events_db to get all events for a particular sport
    # Get all events for sport name.
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # It is a list of lists
    # Chronologically order them by start
    # events_db = [
    #    ['1km Women\'s Cycle', '1800', 'Cycling', 'Velodrome', 'W', '0401'],
    #    ['1km Men\'s Cycle', '1920', 'Cycling', 'Velodrome', 'X', '1432']
    #]

    # Format:
    # [
    #   [name, start, sport, venue_name, gender, event_id]
    # ]
    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        sql = """SELECT event_name, event_start, sport_name, place_name, event_gender, event_id
                FROM (event INNER JOIN place ON event.sport_venue = place.place_id) NATURAL JOIN sport
                WHERE LOWER(sport_name) = %s
                ORDER BY event_start;"""
        cur.execute(sql, (sportname,))
        events_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if events_db is None:
        events = [{
            'name': None,
            'start': None,
            'sport': None,
            'venue': None,
            'gender': None,
            'event_id': None
        }]
        return events

    events = [{
        'name': row[0],
        'start': row[1],
        'sport': row[2],
        'venue': row[3],
        'gender': row[4],
        'event_id': row[5]
    } for row in events_db]

    return events

'''
Get all of the events a certain member is participating in.
'''
def get_events_for_member(member_id):

    # TODO - update the events_db variable to pull from the database
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # It is a list of lists
    # Chronologically order them by start

    # Format:
    # [
    #   [name, start, sport, venue_name, gender]
    # ]

    # events_db = [
    #    ['1km Women\'s Cycle', '1800', 'Cycling', 'Velodrome', 'W'],
    #    ['1km Men\'s Cycle', '1920', 'Cycling', 'Velodrome', 'X']
    #]

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()
    try:
        sql = """SELECT event_name, event_start, sport_name, place_name, event_gender
                FROM  (event NATURAL JOIN participates INNER JOIN place ON event.sport_venue = place.place_id) NATURAL JOIN sport
                WHERE athlete_id = %s
                ORDER BY event_start"""
        cur.execute(sql, (member_id,))
        events_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if events_db is None:
        events = [{
            'name': None,
            'start': None,
            'sport': None,
            'venue': None,
            'gender': None
        }]
        return events

    events = [{
        'name': row[0],
        'start': row[1],
        'sport': row[2],
        'venue': row[3],
        'gender': row[4]
    } for row in events_db]

    return events

'''
Get event information for a certain event
'''
def event_details(eventname):
    # TODO - update the event_db to get that particular event
    # Get all events for sport name.
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # It is a list of lists
    # Chronologically order them by start

    # Format:
    #   [name, start, sport, venue_name, gender]

    # event_db = ['1km Women\'s Cycle', '1800', 'Cycling', 'Velodrome', 'W']

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """SELECT event_name, TO_CHAR(EXTRACT(HOUR FROM event_start), 'FM00') || TO_CHAR(EXTRACT(MINUTE FROM event_start), 'FM00'), sport_name, place_name, event_gender
                FROM  (event JOIN place ON event.sport_venue = place.place_id) NATURAL JOIN sport
                WHERE event_name = %s
                ORDER BY event_start """
        cur.execute(sql, (eventname,))
        event_db = cur.fetchone()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if event_db is None:
        event = {
            'name' : None,
            'start': None,
            'sport': None,
            'venue': None,
            'gender': None
        }
        return event
    event = {
        'name' : event_db[0],
        'start': event_db[1],
        'sport': event_db[2],
        'venue': event_db[3],
        'gender': event_db[4]
    }

    return event



#####################################################
## Results
#####################################################

'''
Get the results for a given event.
'''
def get_results_for_event(event_name):

    # TODO - update the results_db to get information from the database!
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # This should return a list of who participated and the results.

    # This is a list of lists.
    # Order by ranking of medal, then by type (e.g. points/time/etc.)

    # Format:
    # [
    #   [member_id, result, medal],
    #   ...
    # ]

    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

 #   results_db = [
#        ['1234567890', '10pts', 'Gold'],
#        ['8761287368', '8pts', 'Silver'],
#        ['1638712633', '5pts', 'Bronze'],
#        ['5873287436', '4pts', ''],
#        ['6328743234', '4pts', '']
#    ]

    try:
        sql = """SELECT athlete_id, result_type, medal
                 FROM participates NATURAL JOIN event
                 WHERE event_name = %s;"""
        cur.execute(sql, (event_name,))
        results_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if results_db is None:
        results =[{
            'member_id': None,
            'result': None,
            'medal': None
        }]
        return results

    for i in range(0, len(results_db)):
        if (results_db[i][2] == 'B'):
            results_db[i][2] = 'Bronze'
        elif (results_db[i][2] == 'S'):
            results_db[i][2] = 'Silver'
        elif (results_db[i][2] == 'G'):
            results_db[i][2] = 'Gold'
        elif (results_db[i][2] == None):
            results_db[i][2] = ''
        if (results_db[i][1] == None):
            results_db[i][1] = ''
        if (results_db[i][0] == None):
            results_db[i][0] = ''

    results =[{
        'member_id': row[0],
        'result': row[1],
        'medal': row[2]
    } for row in results_db]

    return results

'''
Get all the officials that participated, and their positions.
'''
def get_all_officials(event_name):
    # TODO
    # Return the data (NOTE: look at the information, requires more than a simple select. NOTE ALSO: ordering of columns)
    # This should return a list of who participated and their role.

    # This is a list of lists.

    # [
    #   [member_id, role],
    #   ...
    # ]

    #officials_db = [
#        ['1234567890', 'Judge'],
#        ['8761287368', 'Medal Holder'],
#        ['1638712633', 'Random Bystander'],
#        ['5873287436', 'Umbrella Holder'],
#        ['6328743234', 'Marshall']
#    ]


    conn = database_connect()
    if (conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """SELECT member_id, role
                 FROM runsevent NATURAL JOIN event
                 WHERE event_name = %s;"""
        cur.execute(sql, (event_name,))
        officials_db = cur.fetchall()

    except:
        # If there were any errors, return a NULL row printing an error to the debug
        return None

    if officials_db is None:
        officials = [{
            'member_id': None,
            'role': None
        }]
        return officials

    for i in range(0, len(officials_db)):
        if (officials_db[i][1] == None):
            officials_db[i][1] = ''
        if (officials_db[i][0] == None):
            officials_db[i][0] = ''

    officials = [{
        'member_id': row[0],
        'role': row[1]
    } for row in officials_db]


    return officials

# =================================================================
# =================================================================

#  FOR MARKING PURPOSES ONLY
#  DO NOT CHANGE

def to_json(fn_name, ret_val):
    return {'function': fn_name, 'res': json.dumps(ret_val)}

# =================================================================
# =================================================================
