from flask import Flask, request
from flask_cors import CORS
import requests
import time
import math
import json
import random

app = Flask(__name__)
CORS(app)

@app.route('/bubbles_script', methods=['POST'])
def run_script():

    data = request.get_json()
    # Chosen interval (in minutes)
    chosenInterval = int(data['stockDeltaPTimespan'])

    # Getting list of all NASDAQ-traded stocks
    url = 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt'
    response = requests.get(url)
    lines = response.text.split('\n')

    # Extracting the names of all stocks
    nasdaq_stocks = [line.split('|')[1] for line in lines if "Common Stock" in line]

    # API URL for historical data
    hist_endpoint = 'https://finnhub.io/api/v1/stock/candle'

    # API URL for current data
    current_endpoint = 'https://finnhub.io/api/v1/quote'

    # API key
    api_key = 'cfpbm11r01qq927hfap0cfpbm11r01qq927hfapg'

    # How many API requests can be made
    api_rateLimit = 30

    # Amount of stocks to be rendered
    rankingAmount = 200
    topStockPicks = False

    # Update bubble stock on interval (in seconds) for smooth bubble animation
    bubblesUpdateInterval = 1/0.25

    # Amount a bubbles stock will need to update before the script comes back to the stock
    bubblesUpdateAmount = math.ceil((rankingAmount/api_rateLimit)*bubblesUpdateInterval)

    # To bubbles format
    bubbles_JSON = []
    bubbles_JSON2 = []
    bubbles_JSONString = ""

    def bubblesUpdate(stock):
        # Stock symbol
        symbol = stock

        # Interval (in seconds)
        interval = chosenInterval * 60
        print(chosenInterval)
        print("hello")

        # Set the current time
        current_time = int(time.time())

        # Set the start and end times for the historical data request
        start_time = current_time - interval
        end_time = current_time

        # Set the resolution to 1 minute
        resolution = '1'
        # Set the number of data points to retrieve to 1
        limit = '1'
        format = 'json'

        # Set the parameters for the historical data API request
        hist_params = {
            'symbol': symbol,
            'resolution': resolution,
            'from': start_time,
            'to': end_time,
            'limit': limit,
            'format': format,
            'token': api_key
        }

        # Send the historical data API request and get the response
        def histResponse():
            hist_response = requests.get(hist_endpoint, params=hist_params)
            return hist_response
        hist_response = histResponse()

        def hist_data_JSONError(hist_response):
            try:
                # Parse the response as JSON
                hist_data = hist_response.json()
                print('AYUP2')
                print(hist_data)
            except json.JSONDecodeError as e:
                # Handle any JSON syntax errors
                print(f"JSON syntax error: {e}")
                return True
            return hist_data
        if hist_data_JSONError(hist_response) == True:
            return
        hist_data = hist_data_JSONError(hist_response)

        def noDataOrError(hist_data,hist_response):
            
            print('AYO?')
            print(json.dumps(hist_data))
            print('AYUP')
            if 'no_data' in json.dumps(hist_data):
                print('here3')
                # Use in real run
                return True
                # Use in practice
                #return False
            if 'error' in json.dumps(hist_data):
                print('here4')
                time.sleep(5)
                hist_response = histResponse()
                hist_data = hist_data_JSONError(hist_response)
                noDataOrError(hist_data,hist_response)
            return False
        print('AYUP3')
        noDataOrError(hist_data,hist_response)
        if noDataOrError(hist_data,hist_response) == True or 'no_data' in json.dumps(hist_data):
            return
        print(json.dumps(hist_data))
        print('AYUP4')

            
        # Get the price and volume from 5 minutes ago
        random_number = random.randint(1, 8)
        price_interval_ago = hist_data['c'][0] #hist_data['c'][0] #10-random_number
        volume_interval_ago = hist_data['v'][0] #hist_data['v'][0] #10-random_number
        current_price = hist_data['c'][-1] #hist_data['c'][-1] #30-random_number
        current_volume = hist_data['v'][-1] #hist_data['v'][-1] #50-random_number
        deltaP = ((current_price/price_interval_ago)*100)-100
        deltaV = ((current_volume/volume_interval_ago)*100)-100

        # Print the results
        # print(f'Price {chosenInterval} minutes ago: {price_interval_ago:.2f}')
        # print(f'Volume {chosenInterval} minutes ago: {volume_interval_ago:,}')
        # print(f'Current price: {current_price:.2f}')
        # print(f'Current volume: {current_volume:,}')
        # print(f'{chosenInterval} minute P change: {deltaP}')
        # print(f'{chosenInterval} minute V change: {deltaV}')

        # To bubbles format
        stock_JSON = {
            'symbol': symbol,
            'price': current_price,
            'volume': current_volume,
            'delta_p': deltaP,
            'delta_t': end_time,
            'delta_v': deltaV,
            'price_interval_ago': price_interval_ago,
            'volume_interval_ago': volume_interval_ago
        }
        #global bubbles_JSON
        #global bubbles_JSONString
        # stock_JSONString = json.dumps(stock_JSON)
        # bubbles_JSONString = bubbles_JSONString + stock_JSONString + ','

        if topStockPicks == True:
            # for i in range(math.ceil(bubblesUpdateAmount)):
            #     print(i+1)
            #     print(bubblesUpdateAmount)
            #     bubbles_JSONUpdate = {
            #         'symbol': symbol,
            #         'price': price_interval_ago+((price_interval_ago*deltaP/100)*((i+1)/bubblesUpdateAmount)),
            #         'volume': volume_interval_ago+((volume_interval_ago*deltaV/100)*((i+1)/bubblesUpdateAmount)),
            #         'delta_p': deltaP*((i+1)/bubblesUpdateAmount),
            #         'delta_t': start_time+((end_time-start_time)*((i+1)/bubblesUpdateAmount)),
            #         'delta_v': deltaV*((i+1)/bubblesUpdateAmount)
            #     }
            #     bubbles_JSON.append(bubbles_JSONUpdate)
            bubbles_JSON.append(stock_JSON)
        else:
            bubbles_JSON.append(stock_JSON)

        time.sleep(0.1)
        return stock_JSON



    # bubblesUpdate()

    # Names of all stocks
    stockCount = 0
    for stock in nasdaq_stocks:
        if stockCount < 1000:
            print(stock)
            bubblesUpdate(stock)
        stockCount += 1
    #bubblesUpdate('APPL')


    # with open('bubbles.txt', 'w') as file:
    #     # Write a string to the file
    #     file.write(bubbles_JSONString)

    bubbles_JSONString = bubbles_JSONString[:-1]

    # Load the JSON data into a Python object
    # bubbles_JSON = json.loads(bubbles_JSONString)

    # Sort the Python object by the ABSdelta_p data value in descending order
    #sorted_obj = sorted(python_bubbleObj, key=lambda x: x['delta_p'], reverse=True)

    sorted_data = sorted(bubbles_JSON, key=lambda x: abs(x["delta_p"]), reverse=True)
    sorted_data = sorted_data[:200]
    topStockPicks = True

    bubbles_JSON = []
    bubbles_JSON3 = []
    bubbles_JSON4 = []
    dataPointsCount = 0
    for i in range(1):
        current_time2 = int(time.time())
        bubbles_JSON2 = []
        for i in range(len(sorted_data)):
            #bubblesUpdate(sorted_data[i]['symbol'])
            bubbles_JSON2.append(bubblesUpdate(sorted_data[i]['symbol']))
            print(bubblesUpdate(sorted_data[i]['symbol']))
            print("Nani")
            print(json.dumps(bubbles_JSON2))
        bubbles_JSON3 = {current_time2: bubbles_JSON2}
        bubbles_JSON4.append(bubbles_JSON3)
        dataPointsCount += 1
        time.sleep(1)
    print(json.dumps(bubbles_JSON4))
        

    # Open the file in write mode
    with open('./data/bubbles.json', 'w') as file:
        # Write a string to the file
        #json.dump(bubbles_JSON, file)
        json.dump(bubbles_JSON4, file)

    #print(json.dumps(bubbles_JSON))

    #return json.dumps(bubbles_JSON)
    file = open("./data/visualize_out_20210429_181546.json", "r")
    contents = file.read()
    file.close()
    #return json.dumps(bubbles_JSON)
    return json.dumps(bubbles_JSON4)


if __name__ == '__main__':
    app.run()