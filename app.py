# Import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime, timedelta

# Import Flask, jsonify
from flask import Flask, jsonify

# SQLAlchemy DataBase Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

"""Home page - List all routes that are available"""
@app.route("/")
def home():
    return(
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

"""Convert the query results to a dictionary using date as the key and prcp as the value
    Return the JSON representation of the dictionary"""

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a database session object
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date_tuple = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt = dt.datetime.strptime(last_date_tuple[0], '%Y-%m-%d')
    last_date = last_date_dt.date()
    one_year_ago_date = last_date - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago_date).all()
    session.close()

    # Convert the query results to a dictionary
    precipitation = []
    
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)

    # Return the JSON representation of the dictionary
    return jsonify(precipitation)

""" Return a JSON list of stations from the dataset """
@app.route("/api/v1.0/stations")
def stations():
    # Create a database session object
    session = Session(engine)  

    # Perform a query to retrieve the stations data
    results = session.query(Station.station).all()
    session.close()

    # Convert the query results to a list
    stations = [result[0] for result in results]

    # Return jsonified data
    return jsonify(stations)


"""Query the dates and temperature observations of the most active station for the last year of data
    Return a JSON list of temperature observations (TOBS) for the previous year""" 

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a database session object
    session = Session(engine)  

    most_active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count().desc()).first()

    most_active_station = most_active_station[0]

    # Calculate the date 1 year ago from the last data point in the database
    last_date_tuple = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt = dt.datetime.strptime(last_date_tuple[0], '%Y-%m-%d')
    last_date = last_date_dt.date()
    one_year_ago_date = last_date - timedelta(days=365)

    # Perform a query to retrieve the temperature observations data
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == most_active_station).\
            filter(Measurement.date >= one_year_ago_date).all()

    session.close()

    # Convert the query results to a dictionary
    tobs_list = []
    
    for date, tobs in tobs_results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    # Return the JSON representation of the dictionary
    return jsonify(tobs_list)


""" Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

@app.route("/api/v1.0/<start>")
def temp_by_start_date(start):
    # Create a database session object
    session = Session(engine)

    # Perform a query to retrieve the temperature observations data
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    # Convert the query results to a dictionary
    temp_data = []
    date_out_of_range = False

    for min_temp, avg_temp, max_temp in results:
        if min_temp == None or avg_temp == None or max_temp == None:
            date_out_of_range = True
        else:
            temp_dict = {}
            temp_dict['minimum temperature'] = min_temp
            temp_dict['average temperature'] = avg_temp
            temp_dict['maximum temperature'] = max_temp
            temp_data.append(temp_dict)

    # Return the JSON representation of the dictionary
    if date_out_of_range == False:
        return jsonify(temp_data)
    
    # Return the error message if there is no data found in the date range given
    else:
        return jsonify({'error': f'No temperature data found. Date is out of range. Please edit the start date.'}, 404)
    

@app.route("/api/v1.0/<start>/<end>")
def temp_by_start_end_date(start, end):
    # Create a database session object
    session = Session(engine)

    # Perform a query to retrieve the temperature observations data
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Convert the query results to a dictionary
    temp_data = []
    date_out_of_range = False

    for min_temp, avg_temp, max_temp in results:
        if min_temp == None or avg_temp == None or max_temp == None:
            date_out_of_range = True
        else:
            temp_dict = {}
            temp_dict['minimum temperature'] = min_temp
            temp_dict['average temperature'] = avg_temp
            temp_dict['maximum temperature'] = max_temp
            temp_data.append(temp_dict)

    # Return the JSON representation of the dictionary
    if date_out_of_range == False:
        return jsonify(temp_data)
    
    # Return the error message if there is no data found in the date range given
    else:
        return jsonify({'error': f'No temperature data found. Date is out of range. Please edit the date range.'}, 404)

if __name__ == "__main__":
    app.run(debug=True)