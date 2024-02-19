from flask import request, jsonify
from . import app
from .models import fetch_and_serialize_chart_info
from .weightedRank import rank_songs
from flask_cors import CORS  # Import the CORS library

CORS(app)  # Enable CORS for all routes on the app. You can customize it as needed.

@app.route('/get_info', methods=['GET'])
def get_info():
    # Extract query parameters
    years = request.args.getlist('years[]')
    global_chart = request.args.get('global', type=str).lower() if request.args.get('global') else None
    country_chart = request.args.get('country', type=str).lower() if request.args.get('country') else None
    genre_chart = request.args.get('genre', type=str).lower() if request.args.get('genre') else None
    global_weight = request.args.get('globalWeight', type=float)
    country_weight = request.args.get('countryWeight', type=float)
    genre_weight = request.args.get('genreWeight', type=float)

    # Initialize an empty list to collect errors
    errors = []

        # Assuming this structure for charts_info: [(chart_data, weight), (chart_data, weight), ...]
    charts_info = []
    for year in years:  
        for chart_name, weight in [(global_chart, global_weight), (country_chart, country_weight), (genre_chart, genre_weight)]:
            if chart_name:  # Proceed only if chart name is provided
                chart_info, error = fetch_and_serialize_chart_info(chart_name, year)
                if error:
                    errors.append(error)
                else:
                    charts_info.append((chart_info, weight))

    if errors:
        return jsonify({"error": errors[0]}), 400 if errors[0] == "Invalid country name" else 500

    # Preparing the data correctly for rank_songs
    if charts_info:
        chart_data_list, weight_list = zip(*charts_info)  # Separates chart data and weights into two lists
        ranked_list = rank_songs(chart_data_list, weight_list)
        return jsonify(ranked_list)
    else:
        return jsonify({"error": "No valid chart information provided"}), 400
