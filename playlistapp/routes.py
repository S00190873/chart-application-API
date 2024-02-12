from flask import request, jsonify
from . import app
from .models import fetch_and_serialize_chart_info
from .weightedRank import rank_songs

@app.route('/get_info', methods=['GET'])
def get_info():
    Global = request.args.get('country1', type=str)
    CountryName = request.args.get('country2', type=str)
    GlobalWeight = request.args.get('globalweight', type=float)
    CountryWeight = request.args.get('countryweight', type=float)


    GlobalChart, error = fetch_and_serialize_chart_info(CountryName)
    CountryChart, error = fetch_and_serialize_chart_info(Global)

    if error:
        return jsonify({"error": error}), 400 if error == "Invalid country name" else 404
    
    ranked_list = rank_songs(GlobalChart, CountryChart, GlobalWeight, CountryWeight)

    return jsonify(ranked_list)