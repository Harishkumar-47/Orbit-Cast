import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

CSV_FILE = 'district_wise_rainfall_normal.csv'
df = pd.read_csv(CSV_FILE)

MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

# Clean up strings (strip leading/trailing whitespace)
df['STATE_UT_NAME'] = df['STATE_UT_NAME'].str.strip()
df['DISTRICT'] = df['DISTRICT'].str.strip()

def get_month_indices(start_month, end_month):
    """Returns indices for months between start_month and end_month (inclusive)"""
    try:
        i1 = MONTHS.index(start_month)
        i2 = MONTHS.index(end_month)
        if i1 <= i2:
            return list(range(i1, i2+1))
        else:
            # wrap around the year (e.g., NOV to FEB)
            return list(range(i1, 12)) + list(range(0, i2+1))
    except Exception:
        return []

@app.route('/states', methods=['GET'])
def get_states():
    states = sorted(df['STATE_UT_NAME'].unique())
    return jsonify(states)

@app.route('/districts', methods=['GET'])
def get_districts():
    state = request.args.get('state')
    if not state:
        return jsonify([]), 400
    districts = df[df['STATE_UT_NAME'] == state]['DISTRICT'].unique()
    return jsonify(sorted(districts))

@app.route('/rainfall', methods=['GET'])
def get_rainfall():
    state = request.args.get('state')
    district = request.args.get('district')
    month = request.args.get('month')
    if not (state and district and month):
        return jsonify({'error': 'Missing parameters'}), 400
    row = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
    if row.empty:
        return jsonify({'error': 'District not found'}), 404
    rain = float(row.iloc[0][month])
    annual = float(row.iloc[0]['ANNUAL'])
    return jsonify({'rainfall_mm': rain, 'annual_mm': annual})

@app.route('/rainfall_probability', methods=['GET'])
def rainfall_probability():
    state = request.args.get('state')
    district = request.args.get('district')
    month = request.args.get('month')
    threshold = request.args.get('threshold', type=float)
    if not (state and district and month and threshold is not None):
        return jsonify({'error': 'Missing parameters'}), 400
    row = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
    if row.empty:
        return jsonify({'error': 'District not found'}), 404
    rain = float(row.iloc[0][month])
    prob = 100 if rain >= threshold else 0
    variable_difference = rain - threshold
    return jsonify({
        'state': state,
        'district': district,
        'month': month,
        'rainfall_mm': rain,
        'threshold_mm': threshold,
        'probability_percent': prob,
        'variable_difference': round(variable_difference, 2)
    })

@app.route('/rainfall_range_probability', methods=['GET'])
def rainfall_range_probability():
    state = request.args.get('state')
    district = request.args.get('district')
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')
    threshold = request.args.get('threshold', type=float)
    if not (state and district and start_month and end_month and threshold is not None):
        return jsonify({'error': 'Missing parameters'}), 400
    row = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
    if row.empty:
        return jsonify({'error': 'District not found'}), 404
    row = row.iloc[0]
    month_idxs = get_month_indices(start_month, end_month)
    months_in_range = [MONTHS[i] for i in month_idxs]
    values = [float(row[m]) for m in months_in_range]
    avg = sum(values)/len(values) if values else 0
    count_above = sum(1 for v in values if v >= threshold)
    probability = round(100 * count_above / len(values), 2) if values else 0
    variable_difference = avg - threshold
    # Also return per-month probability and difference if needed
    per_month_results = []
    for m, v in zip(months_in_range, values):
        per_prob = 100 if v >= threshold else 0
        per_diff = v - threshold
        per_month_results.append({
            'month': m,
            'rainfall_mm': v,
            'threshold_mm': threshold,
            'probability_percent': per_prob,
            'variable_difference': round(per_diff, 2)
        })
    result = {
        'state': state,
        'district': district,
        'months': months_in_range,
        'rainfall_values_mm': values,
        'average_rainfall_mm': round(avg,2),
        'custom_threshold_mm': threshold,
        'probability_percent': probability,
        'average_minus_threshold': round(variable_difference,2),
        'per_month': per_month_results
    }
    return jsonify(result)

@app.route('/rainfall_monthly', methods=['GET'])
def rainfall_monthly():
    state = request.args.get('state')
    district = request.args.get('district')
    row = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
    if row.empty:
        return jsonify({'error': 'District not found'}), 404
    vals = {m: float(row.iloc[0][m]) for m in MONTHS}
    return jsonify(vals)

if __name__ == '__main__':
    app.run(debug=True)