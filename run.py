# run.py
from playlistapp import app
from playlistapp.utils import check_database_connection

if __name__ == '__main__':
    check_database_connection()
    app.run(debug=True)