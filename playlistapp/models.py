from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from . import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class ChartInfo(db.Model):
    __abstract__ = True
    title = db.Column(db.String(255), primary_key=True)
    artist = db.Column(db.String(255))

    def serialize(self):
        return {
            'Title': self.title,
            'Artist': self.artist
        }

# Dictionary to store already defined model classes
defined_models = {}

def get_chart_info_model(chart_name, year):
    table_name = f'{chart_name}_{year}'.lower()

    if table_name in defined_models:
        return defined_models[table_name]

    chart_info_model = type(f'ChartInfo{chart_name.capitalize()}{year}', (ChartInfo, db.Model), {
        '__tablename__': table_name,
    })

    defined_models[table_name] = chart_info_model

    return chart_info_model

def get_available_years(chart_name):
    available_years = []
    for year in range(2003, 2024):  # Adjust this range based on your data
        chart_info_model = get_chart_info_model(chart_name, year)
        if db.inspect(db.engine).has_table(chart_info_model.__tablename__):
            available_years.append(year)
    return available_years

def get_available_years_for_riaa(certificationType):
    table_name = f'riaa_{certificationType}'
    
    if not db.inspect(db.engine).has_table(table_name):
        return []

    try:
        query = text(f"SELECT DISTINCT release_date AS year FROM {table_name} ORDER BY year")
        result = db.session.execute(query)
        available_years = [row[0] for row in result]
        return available_years
    except Exception as e:
        logging.error(f"Error fetching available years for {certificationType}: {str(e)}")
        return []

def get_available_genres():
    try:
        query = text("SELECT DISTINCT genre FROM riaa_all")
        result = db.session.execute(query)
        genres = [row[0] for row in result]
        return genres
    except Exception as e:
        logging.error(f"Error fetching genres: {str(e)}")
        return []

def get_riaa_data(certificationType, year, genre=None):
    table_names = []
    
    if certificationType == "all":
        table_names = ['riaa_diamond', 'riaa_platinum', 'riaa_gold']
    else:
        table_name = f'riaa_{certificationType}'
        table_names.append(table_name)

    try:
        combined_chart_info = []
        
        for table_name in table_names:
            # Check if the table exists
            if not db.inspect(db.engine).has_table(table_name):
                continue

            # Construct the query string based on the provided year and genre
            query_string = f"SELECT * FROM {table_name}"
            query_params = {}

            if year != "ALL" and year is not None:
                query_string += " WHERE release_date = :year"
                query_params['year'] = year

            if genre and genre != "All Genres":
                if "WHERE" in query_string:
                    query_string += " AND genre = :genre"
                else:
                    query_string += " WHERE genre = :genre"
                query_params['genre'] = genre

            query = text(query_string)
            result = db.session.execute(query, query_params)
            chart_info = [dict(zip(result.keys(), row)) for row in result]
            combined_chart_info.extend(chart_info)
        
        # Check if any data was returned
        if not combined_chart_info:
            return None, "No data found for the specified year, genre, and certification type"

        # Serialize data to include all relevant fields
        serialized_data = [
            {
                'Title': row['title'],
                'Artist': row['artist'],
                'Units': row['units'],
                'Release_Date': row['release_date'],
                'Genre': row['genre'],
                'Award': row['award']
            } 
            for row in combined_chart_info
        ]
        
        return serialized_data, None

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None, "An internal server error occurred"


def fetch_and_serialize_chart_info(chart_name, year):
    chart_info_model = get_chart_info_model(chart_name, year)

    if chart_info_model is None:
        logging.info(f"Invalid chart name: {chart_name}")
        return None, "Invalid chart name"

    try:
        if not db.inspect(db.engine).has_table(chart_info_model.__tablename__):
            logging.info(f"Table does not exist: {chart_info_model.__tablename__}")
            return None, "Requested table does not exist"
        
        chart_info_list = chart_info_model.query.all()

    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")
        return None, f"Database error: {str(e)}"

    if not chart_info_list:
        return None, "Data not found"

    # Include the full table name in the serialized data
    table_name = f"{chart_name}_{year}".lower()
    serialized_data = [
        {
            'Title': item.title,
            'Artist': item.artist,
            'TableName': table_name  # Add the full table name here
        }
        for item in chart_info_list
    ]
    
    return serialized_data, None

def get_riaa_certification_info(title, artist):
    try:
        # Convert title and artist to uppercase to match the database
        title_upper = title.upper()
        artist_upper = artist.upper()

        query = text("""
            SELECT award, units FROM riaa_all 
            WHERE UPPER(title) = :title AND UPPER(artist) = :artist
        """)
        result = db.session.execute(query, {'title': title_upper, 'artist': artist_upper}).fetchone()

        if result:
            award, units = result
            return award, units  # Return award and units directly
        else:
            return None, None  # Return None for both if not found
    except Exception as e:
        logging.error(f"Error fetching RIAA certification for {title} by {artist}: {str(e)}")
        return None, None  # Return None for both if there's an error

