import requests
import argparse

MIN_VOL = 2000
MIN_SPREAD = 3.5

# API endpoint
url = "https://tradeogre.com/api/v1/markets"

parser = argparse.ArgumentParser(description='Automatically sets buy and sell orders when the spread is within range.', )
parser.add_argument(
    "-spread",
    default=MIN_SPREAD,
    help="The min spread to display the ticker",
    required=True
)
parser.add_argument(
    "-vol",
    default=MIN_VOL,
    help="The min vol to display the ticker",
    required=True
)
args = parser.parse_args()

response = requests.get(url)

if response.status_code == 200:
    markets_data_list = response.json()
    
    # Iterate over the list of markets
    for market_data in markets_data_list:

        # Extract the market name and its data
        market_name, data = list(market_data.items())[0]

        # Check if volume is above MIN_VOL constant
        if (float(data['volume']) > float(args.vol)):
            
            # Calculate spread and display Ticker if above MIN_SPREAD
            spread = -round(((float(data['bid']) / float(data['ask']) * 100) - 100), 5)
            if spread > float(args.spread):
                print(f"Market: {market_name}")
                print(f"Spread {spread}")
                print(f"Initial Price: {data['initialprice']}")
                print(f"Price: {data['price']}")
                print(f"High: {data['high']}")
                print(f"Low: {data['low']}")
                print(f"Volume: {data['volume']}")
                print(f"Bid: {data['bid']}")
                print(f"Ask: {data['ask']}")
                print(f"Basename: {data['basename']}")
                print("-------------------------")
else:
    print("Failed to retrieve data from the API")
