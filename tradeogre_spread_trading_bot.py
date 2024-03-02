import requests
import random
import base64
import time
import sys
import argparse
import signal 

CAN_PLACE_ORDERS = True

# API KEYS (EDIT THIS)
API_KEY = ""
API_SECRET = ""

# REFRESH TIME DEFAULT
REFRESH_TIME = 10

# MIN SPREAD TO TRADE DEFAULT
SPREAD_DEFAULT = "3.25"

# ORDER SIZE MIN/MAX DEFAULTS
ORDER_SIZE_MIN = 1
ORDER_SIZE_MAX = 1

# Global vars close your eyes this was quick and dirtty
SELL_ORDER_UUID = ""
BUY_ORDER_UUID = ""
SELL_PRICE = 0
BUY_PRICE = 0

def get_highest_key(kvp):
    high = 0.0
    for key in kvp:
        if float(key) > high:
            high = float(key)
    return high

def get_lowest_key(kvp):
    low = sys.float_info.max
    for key in kvp:
        if float(key) < low:
            low = float(key)
    return low

def get_lowest_index_orders():
    url = "https://tradeogre.com/api/v1/orders/"+MARKET
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        success = data.get("success")
        if success:
            buy_list = data.get("buy")
            sell_list = data.get("sell")

            if buy_list and sell_list:
                highest_buy_index = get_highest_key(buy_list)
                lowest_sell_index = get_lowest_key(sell_list)         
    
                return highest_buy_index, lowest_sell_index
            else:
                print("Buy or sell list is empty")
        else:
            print("API call was not successful")
    else:
        print("Failed to fetch data from API")

def cancel_order(uuid):
    url = "https://tradeogre.com/api/v1/order/cancel"
    data = {
        "uuid": uuid,
    }
    auth_header = "Basic " + base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
    headers = {"Authorization": auth_header}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to cancel order")
    return None      

def place_sell_order(quantity, price):
     url = "https://tradeogre.com/api/v1/order/sell"
     data = {
        "market": MARKET,
        "quantity": quantity,
        "price": price
    }
     auth_header = "Basic " + base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
     headers = {"Authorization": auth_header}
     response = requests.post(url, data=data, headers=headers)

     if response.status_code == 200:
        return response.json()
     else:
        print("Failed to make sell order")
        return None
     
def place_buy_order(quantity, price):
     url = "https://tradeogre.com/api/v1/order/buy"
     data = {
        "market": MARKET,
        "quantity": quantity,
        "price": price
    }
     auth_header = "Basic " + base64.b64encode(f"{API_KEY}:{API_SECRET}".encode()).decode()
     headers = {"Authorization": auth_header}
     response = requests.post(url, data=data, headers=headers)

     if response.status_code == 200:
        return response.json()
     else:
        print("Failed to make buy order")
        return None

def signal_handler(sig, frame):
    CAN_PLACE_ORDERS = False
    time.sleep(1)

    if BUY_ORDER_UUID:
        print("Canceling order: " + BUY_ORDER_UUID)
        cancel_order(BUY_ORDER_UUID)

    if SELL_ORDER_UUID:
        print("Canceling order: " + SELL_ORDER_UUID)
        cancel_order(SELL_ORDER_UUID)

    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automatically sets buy and sell orders when the spread is within range.', )
    parser.add_argument(
        "-market",
        help="The market to trade in ex (AVAX-USDT)",
        required=True
    )
    parser.add_argument(
        "-spread",
        default=SPREAD_DEFAULT,
        help="The minimum spread required to start trading",
    )
    parser.add_argument(
        "-omin",
        default=ORDER_SIZE_MIN,
        help="The minimum order size placed",
    )
    parser.add_argument(
        "-omax",
        default=ORDER_SIZE_MAX,
        help="The maximum order size placed",
    )
    parser.add_argument(
        "-refresh",
        default=REFRESH_TIME,
        help="The interval to refresh the script in seconds"
    )
    parser.add_argument(
        "-sellmode",
        default=False,
        help="Puts the bot into sell only mode"
    )
    parser.add_argument(
        "-buymode",
        default=False,
        help="Puts the bot into buy only mode"
    )
    args = parser.parse_args()
    MARKET = args.market

    signal.signal(signal.SIGINT, signal_handler)

    while 1:
        highest_buy_index, lowest_sell = get_lowest_index_orders()

        if highest_buy_index and lowest_sell:

            spread = -((float(highest_buy_index) / float(lowest_sell) * 100) - 100)
            spread = round(spread, 4)

            print("Highest buy order:", highest_buy_index)
            print("Lowest sell order:", lowest_sell)
            print("Spread:", spread)

            if spread > float(args.spread):
                if args.buymode == False:

                    if str(lowest_sell) == str(SELL_PRICE):
                        print("We are the lowest seller")
                    else:
                        if SELL_ORDER_UUID:
                            print("Canceling order: " + SELL_ORDER_UUID)
                            cancel_order(SELL_ORDER_UUID)
                    
                        if args.omin == args.omax:
                            sell_size = args.omin
                        else:
                            sell_size = random.randint(int(args.omin), int(args.omax))

                        SELL_PRICE = round(float(lowest_sell)-0.00000001, 8)
                        sell_response = place_sell_order(sell_size, SELL_PRICE)

                        print("Placing order for " + str(sell_size) + " for " + str(SELL_PRICE))
                        print(sell_response)
                        
                        if sell_response.get("success"):
                            SELL_ORDER_UUID = sell_response.get("uuid")
                else:
                    print("Not selling, in buy mode aquiring")

                if args.sellmode == False:

                    if str(highest_buy_index) == str(BUY_PRICE):
                        print("We are the highest buyer")
                    else:
                        if BUY_ORDER_UUID:
                            print("Canceling order: " + BUY_ORDER_UUID)
                            cancel_order(BUY_ORDER_UUID)
        
                        if args.omin == args.omax:
                            buy_size = args.omin
                        else:
                            buy_size = random.randint(int(args.omin), int(args.omax))
                        
                        BUY_PRICE  = round(float(highest_buy_index)+0.00000001, 8)
                        
                        if CAN_PLACE_ORDERS:
                            buy_response = place_buy_order(buy_size, BUY_PRICE)
                        
                            print("Placing order for " + str(buy_size) + " for " + str(BUY_PRICE))
                            print(buy_response)

                            if buy_response.get("success"):
                                BUY_ORDER_UUID = buy_response.get("uuid")
                        else:
                            print("Stopping buy order, app closing")
                else:
                    print("Not buying, in sell mode liquidating")
            else:
                print("Waiting for spread to widen")
                
                if SELL_ORDER_UUID:
                    print("Canceling order: " + SELL_ORDER_UUID)
                    cancel_order(SELL_ORDER_UUID)
                    SELL_ORDER_UUID = ""

                if BUY_ORDER_UUID:
                    print("Canceling order: " + BUY_ORDER_UUID)
                    cancel_order(BUY_ORDER_UUID)
                    BUY_ORDER_UUID = ""

        print("\r\n===============================================================\r\n\r\n")
        time.sleep(float(args.refresh))
