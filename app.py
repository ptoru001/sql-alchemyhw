from flask import Flask, jsonify
from flask_restful import Resource, Api
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
station = Base.classes.station
measurement = Base.classes.measurement
session = Session(engine)

app = Flask(__name__)
api = Api(app)


def Average(lst):
    return sum(lst) / len(lst)


class API_HOME(Resource):
    def get(self):
        response = {
            "Total Precipitation per day": "/api/v1.0/precipitation",
            "List of Stations": "/api/v1.0/stations",
            "Temperatures recorded by the most active station": "/api/v1.0/tobs",
            "Temperature stats in the range": "/api/v1.0/<start> and /api/v1.0/<start>/<end>"
        }
        return jsonify(response)


class Precipitation(Resource):
    def get(self):

        last_year = session.query(measurement).order_by(
            measurement.date)[-1].date[:4]
        date_list = []
        prcp_list = []
        for g in session.query(measurement).order_by(measurement.date.desc()):
            if(g.date[:4] == last_year):
                date_list.append(g.date)
                prcp_list.append(g.prcp)
        response = dict(zip(date_list, prcp_list))

        return jsonify(response)


class Stations(Resource):
    def get(self):
        stations = session.query(func.count(measurement.station),
                                 measurement.station).group_by(
            measurement.station).order_by(
            func.count(measurement.station).desc()).all()

        response = dict(stations)

        return jsonify(response)


class Tobs(Resource):
    def get(self):
        stations = session.query(func.count(measurement.station),
                                 measurement.station).group_by(
            measurement.station).order_by(
            func.count(measurement.station).desc()).all()

        most_active = stations[0][1]
        last_year = session.query(measurement).order_by(
            measurement.date)[-1].date[:4]

        response = {}
        for date, temp in session.query(measurement.date,
                                        measurement.tobs).filter(
                measurement.station == most_active).order_by(
                measurement.date.desc()).all():
            if date[:4] == last_year:
                response[date] = temp

        return jsonify(response)


class Date_Range(Resource):
    def get(self, start=None, end=None):
        if (end is None):
            temp_list = []
            for date, temp in session.query(measurement.date, measurement.tobs
                                            ).group_by(measurement.date).all():
                if (datetime.strptime(start, "%Y-%m-%d") <=
                        datetime.strptime(date, "%Y-%m-%d")):
                    temp_list.append(temp)
            response = {
                "TMAX": max(temp_list),
                "TMIN": min(temp_list),
                "TAVG": Average(temp_list)
            }
        else:
            temp_list = []
            for date, temp in session.query(measurement.date, measurement.tobs
                                            ).group_by(measurement.date).all():
                if (datetime.strptime(start, "%Y-%m-%d") <=
                        datetime.strptime(date, "%Y-%m-%d") and
                        datetime.strptime(end, "%Y-%m-%d") >=
                        datetime.strptime(date, "%Y-%m-%d")):
                    temp_list.append(temp)
            response = {
                "TMAX": max(temp_list),
                "TMIN": min(temp_list),
                "TAVG": Average(temp_list)
            }
        return jsonify(response)


api.add_resource(API_HOME, '/')
api.add_resource(Precipitation, '/api/v1.0/precipitation')
api.add_resource(Stations, '/api/v1.0/stations')
api.add_resource(Tobs, '/api/v1.0/tobs')
api.add_resource(Date_Range,
                 '/api/v1.0/<string:start>',
                 '/api/v1.0/<string:start>/<string:end>')

if __name__ == '__main__':
    app.run(debug=True)

'''
-?/api/v1.0/precipitation
Convert the query results to a dictionary using date as the key and prcp as the value.
Return the JSON representation of your dictionary.
->/api/v1.0/stations
Return a JSON list of stations from the dataset
->/api/v1.0/tobs
Query the dates and temperature observations of the most active station for the last year of data.
Return a JSON list of temperature observations (TOBS) for the previous year.
->/api/v1.0/<start> and /api/v1.0/<start>/<end>
Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
'''
