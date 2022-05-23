import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes"""
    return(
    f"Available Routes:<br/>"
    f"Precipitation Data: /api/v1.0/precipitation<br/>"
    f"List of Station Names: /api/v1.0/stations<br/>"
    f"Temperature at Most Active Station: /api/v1.0/tobs<br/>"
    f"Temperature after date yyyy-mm-dd: /api/v1.0/<start><br/>"
    f"Temperature between dates yyyy-mm-dd and yyyy-mm-dd: /api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date <= "2017-08-23").\
    filter(Measurement.date >= "2016-08-23")

    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #Return the JSON representation of your dictionary.
    precipitation = []
    for date, prcp in query:
        prcpdict = {}
        prcpdict["date"] = date
        prcpdict["precipitation"] = prcp
        precipitation.append(prcpdict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    active = session.query(Station.station, Station.name).all()

    session.close()

    #Return a JSON list of stations from the dataset.
    stations = []
    for station, name in active:
        stationdict = {}
        stationdict["station"] = station
        stationdict["name"] = name
        stations.append(stationdict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #Query the dates and temperature observations of the most active station for the last year of data.
    stationstats = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    mostactive = stationstats[0]

    temps = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station == mostactive).filter(Measurement.date <= "2017-08-23").filter(Measurement.date >= "2016-08-23").all()

    session.close()

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    temp = []
    for tobs, date in temps:
        tempdict = {}
        tempdict["tobs"] = tobs
        tempdict["date"] = date
        temp.append(tempdict)

    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def start_temp_find(start):
    session = Session(engine)

    startquery = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    start = []
    for min, avg, max in startquery:
        startdict = {}
        startdict["min"] = min
        startdict["avg"] = avg
        startdict["max"] = max
        start.append(startdict)

    return jsonify(start)

@app.route("/api/v1.0/<start>/<end>")
def startend_temp_find(start, end):

    session = Session(engine)

    startendquery = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    startend = []
    for min, avg, max in startendquery:
        startenddict = {}
        startenddict["min"] = min
        startenddict["avg"] = avg
        startenddict["max"] = max
        startend.append(startenddict)

    return jsonify(startend)

if __name__ == '__main__':
    app.run(debug=True)