from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/price-history', methods=['GET'])
def get_price_history():
    # Retrieving query parameters from the request
    currency_1 = request.args.get('currency_1')
    currency_2 = request.args.get('currency_2')
    start_date = pd.to_datetime(request.args.get('start_date'))
    end_date = pd.to_datetime(request.args.get('end_date'))

    # Reading the data table from the CSV file
    df = pd.read_csv('FXdatabase.csv', index_col=0, parse_dates=True)

    # Looping through the date range and extracting data for each day
    data = []
    for day in pd.date_range(start_date, end_date):
        if day in df.index:
            price1 = df.loc[day, currency_1]
            price2 = df.loc[day, currency_2]
            if not pd.isna(price1) and not pd.isna(price2):
                if currency_1 != 'USD' or currency_2 != 'USD':
                    if currency_1 == 'USD':
                        data.append((day.strftime('%Y-%m-%d'), price2 / price1))
                    elif currency_2 == 'USD':
                        data.append((day.strftime('%Y-%m-%d'), price1 / price2))
                    else:
                        data.append((day.strftime('%Y-%m-%d'), price2 / price1))

    # Returning the formatted data as JSON
    formatted_data = {
        'currency_1': currency_1,
        'currency_2': currency_2,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'price_history': data
    }
    return jsonify(formatted_data)

if __name__ == '__main__':
    app.run(debug=True)