
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import pandas as pd
import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station



app = Flask(__name__)

@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"enter date as yyyy-mm-dd to find max, min, and avg temp one year to date entered<br>"
        f"/api/v1.0/start<br/>"
        f"enter start date and end date as yyyy-mm-dd to find max, min, and avg temp of selected dates<br>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_entry = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_split = last_entry[0].split('-')
    query_date = dt.date(int(date_split[0]), int(date_split[1]), int(date_split[2])) - dt.timedelta(days=366)
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > query_date).order_by(Measurement.date).all()
    session.close()
    precip_data = []
    for data in last_year_data:
        precip_dict = {}
        precip_dict["Date"] = data[0]
        precip_dict["Precipitation"] = data[1]
        precip_data.append(precip_dict)
    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_query = session.query(Station.name, Station.station).all()
    session.close()
    station_data = []
    for data in station_query:
        station_dict = {}
        station_dict['name'] = data[0]
        station_dict['num'] = data[1]
        station_data.append(station_dict)
    return jsonify(station_data)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station_name = most_active_station[0]
    last_entry = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_split = last_entry[0].split('-')
    query_date = dt.date(int(date_split[0]), int(date_split[1]), int(date_split[2])) - dt.timedelta(days=366)
    tobs_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_name).filter(Measurement.date > query_date).all()
    session.close()
    tobs_data = []
    for data in tobs_query:
        tobs_dict = {}
        tobs_dict['date'] = data[0]
        tobs_dict['tobs'] = data[1]
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = start
    date_split = start_date.split('-')
    query_end_date = dt.date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
    query_start_date = query_end_date - dt.timedelta(days=366)
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= query_start_date).filter(Measurement.date <= query_end_date).all()
    session.close()
    temps_list = temps[0]
    temp_dict = {
        'Min_Temp': temps_list[0],
        'Avg_Temp': temps_list[1],
        'Max_Temp': temps_list[2]
    }
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    start_date = start
    end_date = end
    start_date_split = start_date.split('-')
    end_date_split = end_date.split('-')
    query_start_date = dt.date(int(start_date_split[0]), int(start_date_split[1]), int(start_date_split[2]))
    query_end_date = dt.date(int(end_date_split[0]), int(end_date_split[1]), int(end_date_split[2]))
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= query_start_date).filter(Measurement.date <= query_end_date).all()
    session.close()
    temps_list = temps[0]
    temp_dict = {
        'Min_Temp': temps_list[0],
        'Avg_Temp': temps_list[1],
        'Max_Temp': temps_list[2]
    }
    return jsonify(temp_dict)



if __name__ == '__main__':
    app.run(debug=True)