import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the CSV data once at startup
DATA_FILE = 'DailyDelhiClimateTest.csv'
df = pd.read_csv(DATA_FILE, parse_dates=['date'])

@app.route('/climate', methods=['GET'])
def get_climate_data():
    """
    Query climate data by date or date range.
    Usage:
      - /climate?date=2017-01-15
      - /climate?start=2017-01-01&end=2017-01-31
    """
    date = request.args.get('date')
    start = request.args.get('start')
    end = request.args.get('end')
    
    if date:
        # Query by single date
        result = df[df['date'] == date]
    elif start and end:
        # Query by date range
        mask = (df['date'] >= start) & (df['date'] <= end)
        result = df[mask]
    else:
        # Return all data if no filter given
        result = df
    
    return jsonify(result.to_dict(orient='records'))

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get basic statistics for climate columns.
    Usage:
      - /stats?column=meantemp
      - /stats?column=humidity
    """
    column = request.args.get('column')
    if column not in df.columns or column == 'date':
        return jsonify({'error': 'Invalid column name'}), 400
    
    stats = {
        'min': float(df[column].min()),
        'max': float(df[column].max()),
        'mean': float(df[column].mean()),
        'median': float(df[column].median())
    }
    return jsonify(stats)

@app.route('/columns', methods=['GET'])
def get_columns():
    """Get all available columns in the dataset."""
    return jsonify(df.columns.tolist())

if __name__ == '__main__':
    app.run(debug=True)
S