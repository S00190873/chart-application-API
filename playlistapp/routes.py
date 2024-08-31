from flask import request, jsonify
from . import app
from .models import get_riaa_data, fetch_and_serialize_chart_info, get_available_years, get_available_years_for_riaa, get_available_genres
from flask_cors import CORS
import logging
from .weightedRank import rank_songs

# Enable CORS for all routes on the app
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/get_available_years', methods=['GET'])
def get_available_years_route():
    chart_name = request.args.get('chart_name', type=str).lower()
    if not chart_name:
        return jsonify({"error": "Chart name is required"}), 400
    
    available_years = get_available_years(chart_name)
    return jsonify(available_years)

@app.route('/get_available_years_riaa', methods=['GET'])
def get_available_years_riaa():
    certification_type = request.args.get('certificationType', type=str).lower()
    if certification_type not in ['all', 'diamond', 'platinum', 'gold']:
        return jsonify({"error": "Invalid certification type"}), 400
    
    available_years = get_available_years_for_riaa(certification_type)
    return jsonify(available_years)

@app.route('/get_available_genres', methods=['GET'])
def get_genres():
    try:
        genres = get_available_genres()
        return jsonify(genres), 200
    except Exception as e:
        logging.error(f"Error fetching genres: {str(e)}")
        return jsonify({"error": "An error occurred while fetching genres"}), 500

@app.route('/get_riaa_data', methods=['GET'])
def get_riaa_data_route():
    certification_type = request.args.get('certificationType', type=str).lower()
    year = request.args.get('year', type=str)
    genre = request.args.get('genre', type=str)
    
    # Validate certification type
    if certification_type not in ['all','diamond', 'platinum', 'gold']:
        return jsonify({"error": "Invalid certification type"}), 400
    
    # Fetch data
    chart_info, error = get_riaa_data(certification_type, year, genre)
    
    # Handle errors
    if error:
        if error == "No data found for the specified year, genre, and certification type":
            return jsonify({"error": error}), 404
        else:
            return jsonify({"error": error}), 500
    
    return jsonify(chart_info), 200

@app.route('/getchart', methods=['GET'])
def getchart():
    parameter = request.args.get('parameter', type=str).lower() if request.args.get('parameter') else None
    year = request.args.get('year', type=str)
    
    if not parameter or not year:
        return jsonify({"error": "Parameter and year are required"}), 400
    
    chart_info, error = fetch_and_serialize_chart_info(parameter, year)
    
    if error:
        if error == "Requested table does not exist":
            logging.info(f"Table does not exist for parameter: {parameter}, year: {year}")
            return jsonify({"error": error}), 404
        elif error == "Invalid chart name":
            return jsonify({"error": error}), 400
        else:
            return jsonify({"error": error}), 500
    
    return jsonify(chart_info)

@app.route('/get_info', methods=['GET'])
def get_info():
    logging.info(f"Request args: {request.args}")

    years = request.args.getlist('years[]')
    if not years:
        return jsonify({"error": "Years parameter is required"}), 400

    # Convert the string years to integers and find the min and max
    year_start = int(min(years))
    year_end = int(max(years))
    
    # Create a full list of years in the range
    all_years = list(range(year_start, year_end + 1))

    # Extract chart names and weights
    chart_names = [key for key in request.args.keys() if not key.endswith('Weight') and key != 'years[]']
    if not chart_names:
        return jsonify({"error": "At least one chart name is required"}), 400

    weights = {key.replace('Weight', ''): float(request.args.get(key, type=float)) for key in request.args.keys() if key.endswith('Weight')}
    
    if not any(chart_name in weights for chart_name in chart_names):
        return jsonify({"error": "At least one weight is required"}), 400

    errors = []
    charts_info = []

    for year in all_years:  # Iterate through each year in the range
        for chart_name in chart_names:
            logging.info(f"Processing chart name: {chart_name} for year: {year}")
            if chart_name in weights:
                weight = weights[chart_name]
                chart_info, error = fetch_and_serialize_chart_info(chart_name, year)
                if error:
                    if error == "Requested table does not exist":
                        logging.info(f"Skipping missing table for {chart_name} in {year}.")
                        continue
                    else:
                        logging.info(f"Error fetching data for {chart_name} in {year}: {error}")
                        errors.append(f"Error fetching data for {chart_name} in {year}: {error}")
                else:
                    charts_info.append((chart_info, weight))

    if charts_info:
        chart_data_list, weight_list = zip(*charts_info)
        ranked_list = rank_songs(chart_data_list, weight_list)
        return jsonify(ranked_list)
    else:
        return jsonify({"error": "No valid chart information provided"}), 400
