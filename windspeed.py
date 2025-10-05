import os
import logging
from flask import Flask, request, jsonify, abort
import pandas as pd

def create_app(config=None):
    app = Flask(__name__)

    # Configuration (if needed)
    if config:
        app.config.update(config)

    # Logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # Load dataset
    CSV_FILE = app.config.get('CSV_FILE', 'district_wise_rainfall_normal.csv')
    if not os.path.isfile(CSV_FILE):
        app.logger.error(f"CSV file {CSV_FILE} not found.")
        raise FileNotFoundError(f"CSV file {CSV_FILE} not found.")
    df = pd.read_csv(CSV_FILE)

    # Standardize / clean up
    df['STATE_UT_NAME'] = df['STATE_UT_NAME'].astype(str).str.strip()
    df['DISTRICT'] = df['DISTRICT'].astype(str).str.strip()

    MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    @app.route('/states', methods=['GET'])
    def get_states():
        states = sorted(df['STATE_UT_NAME'].unique())
        return jsonify({'states': states})

    @app.route('/districts', methods=['GET'])
    def get_districts():
        state = request.args.get('state')
        if not state:
            return jsonify({'error': 'Missing “state” parameter'}), 400

        # Normalize
        state = state.strip()
        sub = df[df['STATE_UT_NAME'] == state]
        if sub.empty:
            return jsonify({'error': f'State "{state}" not found'}), 404

        districts = sorted(sub['DISTRICT'].unique())
        return jsonify({'state': state, 'districts': districts})

    @app.route('/rainfall', methods=['GET'])
    def get_rainfall():
        state = request.args.get('state')
        district = request.args.get('district')
        month = request.args.get('month', '').upper()

        if not (state and district and month):
            return jsonify({'error': 'Missing “state”, “district” or “month” parameter'}), 400

        state = state.strip()
        district = district.strip()

        if month not in MONTHS and month != 'ANNUAL':
            return jsonify({'error': f'Month must be one of {MONTHS} or “ANNUAL”'}), 400

        sub = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
        if sub.empty:
            return jsonify({'error': f'Data for state={state}, district={district} not found'}), 404

        try:
            value = float(sub.iloc[0][month])
        except (KeyError, ValueError) as e:
            app.logger.error(f"Error fetching rainfall for {state}, {district}, {month}: {e}")
            return jsonify({'error': 'Internal server error retrieving data'}), 500

        # If month is not "ANNUAL", also include annual
        annual = None
        if month != 'ANNUAL' and 'ANNUAL' in sub.columns:
            try:
                annual = float(sub.iloc[0]['ANNUAL'])
            except Exception:
                annual = None

        resp = {
            'state': state,
            'district': district,
            'month': month,
            'rainfall_mm': value,
        }
        if annual is not None:
            resp['annual_mm'] = annual

        return jsonify(resp)

    @app.route('/rainfall_probability', methods=['GET'])
    def rainfall_probability():
        state = request.args.get('state')
        district = request.args.get('district')
        month = request.args.get('month', '').upper()
        threshold = request.args.get('threshold', type=float)

        if not (state and district and month and threshold is not None):
            return jsonify({'error': 'Missing “state”, “district”, “month” or “threshold” parameter'}), 400

        state = state.strip()
        district = district.strip()
        if month not in MONTHS:
            return jsonify({'error': f'Month must be one of {MONTHS}'}), 400

        sub = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
        if sub.empty:
            return jsonify({'error': f'Data for state={state}, district={district} not found'}), 404

        try:
            rainfall_val = float(sub.iloc[0][month])
        except (KeyError, ValueError):
            return jsonify({'error': 'Error retrieving rainfall data'}), 500

        # For a simple model: if rainfall ≥ threshold → 100% else 0%
        prob = 100.0 if rainfall_val >= threshold else 0.0

        resp = {
            'state': state,
            'district': district,
            'month': month,
            'rainfall_mm': rainfall_val,
            'threshold_mm': threshold,
            'probability_percent': prob
        }
        return jsonify(resp)

    @app.route('/rainfall_monthly', methods=['GET'])
    def rainfall_monthly():
        state = request.args.get('state')
        district = request.args.get('district')

        if not (state and district):
            return jsonify({'error': 'Missing “state” or “district” parameter'}), 400

        state = state.strip()
        district = district.strip()

        sub = df[(df['STATE_UT_NAME'] == state) & (df['DISTRICT'] == district)]
        if sub.empty:
            return jsonify({'error': f'Data for state={state}, district={district} not found'}), 404

        try:
            monthly_vals = {m: float(sub.iloc[0][m]) for m in MONTHS}
        except Exception as e:
            app.logger.error(f"Error retrieving monthly data: {e}")
            return jsonify({'error': 'Internal error retrieving data'}), 500

        resp = {
            'state': state,
            'district': district,
            'monthly_rainfall_mm': monthly_vals
        }
        return jsonify(resp)

    # Optionally: health check / root
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({'message': 'Rainfall API is running.'})

    return app


if __name__ == '__main__':
    # In production you won’t do debug=True and will use a WSGI server (gunicorn, etc.)
    app = create_app({'CSV_FILE': 'district_wise_rainfall_normal.csv'})
    app.run(host='0.0.0.0', port=5000, debug=True)
