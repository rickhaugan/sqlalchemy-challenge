import numpy as np
import datetime
import sqlalchemy
import pandas as pd
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
    prcp = "/api/v1.0/precipitation"
    stns = "/api/v1.0/stations"
    tobs = "/api/v1.0/tobs"
    startend = "/api/v1.0/2016-08-23/2017-08-23"
    return (
        f"""
Welcome to the Hawaii Climate Analysis API!<br>
Available Routes:<br>
<a href='{prcp}'>{prcp}</a><br>
<a href='{stns}'>{stns}</a><br>
<a href='{tobs}'>{tobs}</a><br>
<a href='{startend}'>{startend}</a>
"""
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query measurement date and precipitation
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    results_dict = dict(results)    
    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    results_list = list(np.ravel(results))
    return jsonify(results_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all temps for the most active station
    results = session.query(Measurement.tobs).filter(Measurement.station=="USC00519281").filter(Measurement.date >="2016-08-23").all()

    session.close()

    results_list = list(np.ravel(results))
    return jsonify(results_list)


#route has start and end date, if not given start and end date uses default values
@app.route("/api/v1.0/<start>/<end>")
def weatherdata(start, end):
    startdate = start
    enddate = end
    session = Session(engine)
    if type(enddate) is not datetime.date:
        #default end date
        enddate = "2020-08-31"

        sel = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
        minmaxavg = session.query(*sel).filter(Measurement.date >=startdate).all()
        results_list = list(np.ravel(minmaxavg)) 
        return jsonify(results_list)

    if type(startdate) is not datetime.date:
        #default start date
        startdate = "1950-08-31"
    

    sel = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    minmaxavg = session.query(*sel).filter(Measurement.date >=startdate).filter(Measurement.date <=enddate).all()
    results_list = list(np.ravel(minmaxavg)) 
        

    session.close()

    return jsonify(results_list)



if __name__ == '__main__':
    app.run(debug=True)
