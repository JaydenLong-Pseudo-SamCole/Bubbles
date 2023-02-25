from flask import Flask, request
from flask_cors import CORS
import requests
import time
import math
import json
import random
import datetime as dt

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
    #hist_endpoint = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{from_date}/{to_date}?apiKey=<your API key>"

    # API URL for current data
    #current_endpoint = 'https://finnhub.io/api/v1/quote'

    # API key
    api_key = 'FF3L2jIzaz621a5yNwdsA7FWhkRZcO3z'

    # How many API requests can be made
    #api_rateLimit = 30

    # Amount of stocks to be rendered
    rankingAmount = 200
    topStockPicks = False

    # Update bubble stock on interval (in seconds) for smooth bubble animation
    #bubblesUpdateInterval = 1/0.25

    # Amount a bubbles stock will need to update before the script comes back to the stock
    #bubblesUpdateAmount = math.ceil((rankingAmount/api_rateLimit)*bubblesUpdateInterval)

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

        # Test interval to minus start and end time by for testing to go back to when trading hours were (in seconds)
        test_interval = 30600
        # Set the current time
        current_time = int(time.time()) - test_interval
        print(current_time)

        start_time = (int(dt.datetime.timestamp(dt.datetime.now() - dt.timedelta(minutes=5))) - test_interval)*1000
        print(start_time)
        end_time = (int(dt.datetime.timestamp(dt.datetime.now())) - test_interval)*1000
        print(end_time)
        # API URL for historical data
        hist_endpoint = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_time}/{end_time}?apiKey={api_key}"

        # Set the start and end times for the historical data request
        #start_time = current_time - interval
        #end_time = current_time

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

        def hist_data_JSONError():
            # Send the historical data API request and get the response
            #hist_response = requests.get(hist_endpoint, params=hist_params)
            hist_response = requests.get(hist_endpoint)
            #hist_response.raise_for_status()
            try:
                # Parse the response as JSON
                hist_data = hist_response.json()
                print('AYUP2')
                print(hist_data)
                return hist_data
            except json.JSONDecodeError as e:
                # Handle any JSON syntax errors
                print(f"JSON syntax error: {e}")
                return False
        hist_data = hist_data_JSONError()
        if hist_data == False:
            return False

        # def noDataOrError(hist_data):
            
        #     if hist_data == False:
        #         return False
        #     print('AYO?')
        #     print(json.dumps(hist_data))
        #     print('AYUP')
        #     if 'no_data' in json.dumps(hist_data):
        #         print('here3')
        #         # Use in real run
        #         return False
        #         # Use in practice
        #         #return False
        #     if 'error' in json.dumps(hist_data):
        #         print('here4')
        #         time.sleep(20)
        #         hist_data = hist_data_JSONError()
        #         return noDataOrError(hist_data)
        #     print('AYO?6')
        #     print(json.dumps(hist_data))
        #     print('AYUP6')
        #     return hist_data
        # print('AYUP3')
        # #noDataOrError(hist_data,hist_response)
        # hist_data = noDataOrError(hist_data)
        # if hist_data == False:
        #     return False

        print(json.dumps(hist_data))
        print('AYUP4')

            
        # Get the price and volume from 5 minutes ago
        random_number = random.randint(1, 8)
        try:
            value = hist_data["results"]
        except KeyError:
            print(f"No Data")
            return
        print(hist_data["results"])
        price_interval_ago = hist_data["results"][0]["c"] #hist_data['c'][0] #10-random_number
        volume_interval_ago = hist_data["results"][0]["v"] #hist_data['v'][0] #10-random_number
        current_price = hist_data["results"][-1]["c"] #hist_data['c'][-1] #30-random_number
        current_volume = hist_data["results"][-1]["v"] #hist_data['v'][-1] #50-random_number
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
            'stock': symbol,
            'price': current_price,
            'volume': current_volume,
            'delta_p': deltaP,
            'delta_t': end_time,
            'delta_v': deltaV
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
        # Do no if statement limit for real run, this is just the make is faster for testing
        if stockCount < 15:
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
    # sort it by 200 for real test
    sorted_data = sorted_data[:30]
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
            bubblesUpdate_result = bubblesUpdate(sorted_data[i]['stock'])
            if bubblesUpdate_result != False:
                bubbles_JSON2.append(bubblesUpdate_result)
                print(bubblesUpdate(sorted_data[i]['stock']))
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