from flask import Flask, request
from flask_cors import CORS
import requests
import time
import math
import json
import random
import datetime as dt
import multiprocessing
import numpy as np
from threading import Thread



app = Flask(__name__)
CORS(app)

@app.route('/bubbles_script', methods=['POST'])
def run_script():

    data = request.get_json()
    # Equivalent to about 2 years of stock callback, assuming we will only ever do a maximum of 1 year or so, meaning the user tried to change the HTML in the inspector
    if (int(data['stockDeltaPTimespan']) > 1000000):
        return "Oi m8! Trying to overload the server, ey?"
    def run_bubbles(result_list, currentCPUProcess, maxCPUProcesses):
        # Chosen interval (in minutes)
        chosenInterval = int(data['stockDeltaPTimespan'])
        # The top 200 stocks, will be null if the user just started the session because it hasn't sorted through 5,000+ stocks yet
        topStockData = data['stockData']
        print(chosenInterval)
        print(topStockData)

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

        # Get the stock quotes and update them continously
        def bubblesUpdate(stock, countOfStockTries):
            # Stock symbol
            symbol = stock

            # Interval (in seconds)
            choseIntervalFormated = chosenInterval*60
            #print("hello")

            # Test interval to minus start and end time by for testing to go back to when trading hours were (in seconds)
            test_interval = 0
            # Set the current time
            current_time = int(time.time()) - test_interval
            #print(current_time)

            # start_time = (int(dt.datetime.timestamp(dt.datetime.now() - dt.timedelta(minutes=chosenInterval))) - test_interval)*1000
            start_time = 1678212049000-(countOfStockTries*10*1000)
            #print(start_time)
            # end_time = (int(dt.datetime.timestamp(dt.datetime.now())) - test_interval)*1000
            end_time = 1678212349000-(countOfStockTries*10*1000)
            #print(end_time)
            
            # Timestamp to start getting stock quotes, current time minus the interval(minutes ago) the user selected
            start_timestamp_data = dt.datetime.fromtimestamp(current_time-choseIntervalFormated)
            start_formatted_date = start_timestamp_data.strftime('%Y-%m-%d')
            # Timestamp of current stock quote in the current time, to calculate the difference in P/V from the first timestamp data point, to the newest data point 
            end_timestamp_data = dt.datetime.fromtimestamp(current_time)
            end_formatted_date = end_timestamp_data.strftime('%Y-%m-%d')
            # API URL for historical data
            hist_endpoint = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start_formatted_date}/{end_formatted_date}?apiKey={api_key}"

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

            # Check if any errors occur while retrieving a quote, if not, put the response in "hist_data"
            def hist_data_JSONError():
                # Send the historical data API request and get the response
                #hist_response = requests.get(hist_endpoint, params=hist_params)
                hist_response = requests.get(hist_endpoint)
                #hist_response.raise_for_status()
                try:
                    # Parse the response as JSON
                    hist_data = hist_response.json()
                    #print('AYUP2')
                    #print(hist_data)
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

            #print(json.dumps(hist_data))
            #print('AYUP4')

                
            # Get the price and volume from 5 minutes ago
            #random_number = random.randint(1, 8)
            
            # Get a specific index of the returned response, but if this index is not there, it means the stock has no data (meaning it's not a stock that's traded, and thus NasDaq doesn't update it)
            try:
                value = hist_data["results"]
                countOfStockTries = 0
            except KeyError:
                print(f"No Data {stock}")
                countOfStockTries += 1
                # if (countOfStockTries > 50):
                #     return False
                # return bubblesUpdate(stock, countOfStockTries)
                return False
            #print(hist_data["results"])
            stockTimeIndex = 2
            # Return False if there is no data from the start time to current time within the desired interval OR if the total volume is below 100,000
            if len(hist_data["results"]) < stockTimeIndex or hist_data["results"][-1]["v"] < 1000:
            # if len(hist_data["results"]) < stockTimeIndex:
                return False
            # Since the quote can return a varying number of candles depending on the stock (it can return three candles in a five minute-interval, or six, or just two, etc..). This code gets the last stock quote and keeps searching the index from end-to-start until it finds another quote with a timestamp equal to, or greater than, the interval the user selected
            while ((hist_data["results"][-1]["t"])-(hist_data["results"][-stockTimeIndex]["t"])) < (choseIntervalFormated*1000):
                stockTimeIndex += 1
                if len(hist_data["results"]) < stockTimeIndex:
                    return False
                if (stockTimeIndex > 100000):
                    print("M8, Too many candles *sad_pepe_face*")
                    return False
            price_interval_ago = hist_data["results"][-stockTimeIndex]["c"] #hist_data['c'][0] #10-random_number
            #print(f'{stock} interval ago {price_interval_ago} and {hist_data["results"][-stockTimeIndex]["t"]}')
            volume_interval_ago = hist_data["results"][-stockTimeIndex]["v"] #hist_data['v'][0] #10-random_number
            current_price = hist_data["results"][-1]["c"] #hist_data['c'][-1] #30-random_number
            #print(f'{stock} NOW ago {current_price} and {hist_data["results"][-1]["t"]}')
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

            #time.sleep(0.1)
            return stock_JSON
        
        # Compile all the stocks itgot from each iteration of the bubblesUpdate loop into a singular JSON
        def JSONToBeSentToApp(stocksSorted):
            bubbles_JSON = []
            bubbles_JSON3 = []
            bubbles_JSON4 = []
            current_time2 = int(time.time())
            bubbles_JSON2 = []
            for i in range(len(stocksSorted)):
                #bubblesUpdate(stocksSorted[i]['symbol'])
                bubblesUpdate_result = bubblesUpdate(stocksSorted[i]['stock'], 0)
                if bubblesUpdate_result != False:
                    bubbles_JSON2.append(bubblesUpdate_result)
                    #print(bubblesUpdate(stocksSorted[i]['stock']))
                    #print("Nani")
                    #print(json.dumps(bubbles_JSON2))
                else:
                    print("was FAlsE")
                    bubbles_JSON2.append(stocksSorted[i])

            #bubbles_JSON3 = {current_time2: bubbles_JSON2}
            #bubbles_JSON4.append(bubbles_JSON2)
            #print(json.dumps(bubbles_JSON4))
            # Open the file in write mode
            # with open('./data/bubbles.json', 'w') as file:
            #     # Write a string to the file
            #     json.dump(bubbles_JSON4, file)
            return bubbles_JSON2

        # if the top 200 stocks have already been selected, only search and update those in the bubblesUpdate function, else, scan through all 5,000+ stocks and find the top 200 absolute value performers 
        if topStockData != "null":
            topStockData = "[" + (((json.dumps(topStockData)).split("["))[2])[:-3] + "]"
            topStockData = json.loads(topStockData)
            np_topStockData = np.array(topStockData)
            split_topStockData = np.array_split(np_topStockData, maxCPUProcesses)
            # Loop through each of the top 200 stocks, but only for a certain segment of the list (determined by which CPU thread we're on, e.g. if we're on the 4th CPU thread out of 8, it would choose a array of stocks somewhere in the middle of the stock list on the top 200 list)
            bubbles_JSON4 = JSONToBeSentToApp(split_topStockData[currentCPUProcess-1])
        else:
            # Names of all stocks
            np_nasdaq_stocks = np.array(nasdaq_stocks)
            split_nasdaq_stocks = np.array_split(np_nasdaq_stocks, maxCPUProcesses)
            stockCount = 0
            # Loop through each stocks to get its quotes, but only for a certain segment of the total number of stocks on the NasDaq (determined by which CPU thread we're on, e.g. if we're on the 4th CPU thread out of 8, it would choose a array of stocks somewhere in the middle of the stock list on the NasDaq)
            for stock in split_nasdaq_stocks[currentCPUProcess-1]:
                # Do no if statement limit for real run, this is just the make is faster for testing
                #if stockCount < 40:
                print(stock)
                print(stockCount)
                bubblesUpdate(stock, 0)
                stockCount += 1
            #bubblesUpdate('APPL')

            # Sort the stocks by absolute P value
            sorted_data = sorted(bubbles_JSON, key=lambda x: abs(x["delta_p"]), reverse=True)
            # Only take the top 200
            sorted_data = sorted_data[:(math.floor(200*(1/maxCPUProcesses)))]
            topStockPicks = True

            bubbles_JSON4 = JSONToBeSentToApp(sorted_data)
        
        result_list.append(json.dumps(bubbles_JSON4))
        #return json.dumps(bubbles_JSON4)
        
    # Create a pool of worker processes
    # num_processes = multiprocessing.cpu_count()
    # pool = multiprocessing.Pool(num_processes)
    
    # # Define input arguments for each script instance
    # script_args_list = []
    # print(num_processes)
    # for i in range(num_processes):
    #     script_args_list.append((i/num_processes)*num_processes)
    
    # print("args List")
    # print(script_args_list)
    # # Start each script instance as a separate process
    # results = [pool.apply_async(run_bubbles, args=(script_args,num_processes)) for script_args in script_args_list]

    # START, up until "END," the entire section pretty much determines the number of CPU threads available, and runs the part of the script we want on each of those threads, and then compiles all of them together once they've finished, and then sorts them in alphabetical order(so when app.py is run again everytime the Bubbles stocks updates, it will always get back the same list order, which is alphabetical order, so it knows which circle is which stock in the index. It's not sorted by P value because we already have the top 200 stocks based on absolute P value, so sorting by P value wouldn't change anything, and would make it worse as the stocks' positions in the index would change whenever their P values increase or decrease).
    num_instances = multiprocessing.cpu_count()
    result_list = []
    threads = []
    for i in range(num_instances):
        # print("i start")
        # print(i)
        t = Thread(target=run_bubbles, args=(result_list,i+1,num_instances))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Combine the results and return the response
    result_list = [s[1:-1] for s in result_list]
    responseJoin = ','.join(result_list)
    responseSplit = responseJoin.split('},')
    responseSplit = [s + "}" for s in responseSplit[:-1]] + [responseSplit[-1]]
    for i in range(len(responseSplit)):
        responseSplit[i] = json.loads(responseSplit[i])
    response_Sorted = sorted(responseSplit, key=lambda x: x["stock"])
    #responseCompiled = "[{'" + str(int(time.time())) + "': " + str(response_Sorted) + "}]"
    responseCompiled = {int(time.time()): response_Sorted}
    responseCompiledJSON = [responseCompiled]
    print('Wuddap')
    #response2 = response2.replace('\\', '')
    print(json.dumps(responseCompiledJSON))
    # REPLACE (rewrite) the current data in the bubbles JSON with the new update of the stocks
    with open('./data/bubbles.json', 'w') as file:
        # Write a string to the file
        file.write(json.dumps(responseCompiledJSON))


    if (data['stockData'] == "null"):
        with open('./data/bubblesReplaySession.json', 'w') as file:
            file.write('[]')

    with open('./data/bubblesReplaySession.json', 'r') as file:
        bubblesReplaySession = file.read()

    print("Replay session")
    bubblesReplaySession = json.loads(bubblesReplaySession)
    print(json.dumps(bubblesReplaySession))
    bubblesReplaySession.append(responseCompiled)
    # ADD the data to the replay session JSON
    with open('./data/bubblesReplaySession.json', 'w') as file:
        file.write(json.dumps(bubblesReplaySession))

    return json.dumps(responseCompiledJSON)
    # END
    
    # # Wait for all processes to finish
    # pool.close()
    # pool.join()
    
    # # Collect the results from each process
    # output_list = [result.get() for result in results]
    # print("output")
    # print(output_list)
    # return output_list
    


    #print(json.dumps(bubbles_JSON))

    #return json.dumps(bubbles_JSON)
    # file = open("./data/visualize_out_20210429_181546.json", "r")
    # contents = file.read()
    # file.close()
    #return json.dumps(bubbles_JSON)

# If the user clicks the button to replay the session, if will just send back the JSON(JSON2) file location of all the Bubbles stock updates that the script has been adding to everytime it updated the stocks
@app.route('/replaybubblessession', methods=['POST'])
def replayingBubblesSession():
    with open('./data/bubblesReplaySession.json', 'r') as file:
        bubblesReplaySession = file.read()
    return bubblesReplaySession

if __name__ == '__main__':
    app.run()

