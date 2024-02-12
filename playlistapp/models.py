from . import db

class ChartInfo(db.Model):
    __abstract__ = True
    songid = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    songname = db.Column(db.String(255))
    artist = db.Column(db.String(255))

    def serialize(self):
        return {
            'SongID': self.songid,
            'Position': self.position,
            'Songname': self.songname,
            'Artist': self.artist
        }
    
    # Function to dynamically select the appropriate database table based on the country name
def get_chart_info_model(country_name):
    table_name = f'chartinfo{country_name}2023'  # Construct table name based on country_name

    # Create a new model class with the dynamically generated table name
    chart_info_model = type(f'ChartInfo{country_name}2023', (ChartInfo, db.Model), {
        '__tablename__': table_name,
    })
    return chart_info_model

def fetch_and_serialize_chart_info(country_name):
    chart_info_model = get_chart_info_model(country_name)

    if chart_info_model is None:
        return None, "Invalid country name"

    chart_info_list = chart_info_model.query.all()

    if not chart_info_list:
        return None, "Data not found"

    serialized_data = [item.serialize() for item in chart_info_list]
    return serialized_data, None