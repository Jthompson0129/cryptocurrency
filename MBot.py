# import os
# import time
# import uuid
# from coinbase.wallet.client import Client
#
#
# # Configuration parameters
# API_KEY = os.getenv('API_KEY')
# API_SECRET = os.getenv('API_SECRET')
#
# # Initialize Coinbase client
# client = Client(API_KEY, API_SECRET)
#
# # Paper trading configuration
# initial_capital = 200.00  # Total capital for paper trading
# capital = initial_capital
# total_profit = 0.00  # Track total profit since the start of the session
# grid_size = 0.0000005  # Adjust this value based on market conditions
# num_grids = 10  # Total number of buy/sell orders
# investment_amount = 5.00  # Amount in USD per trade
# symbol = 'SHIB-USD'  # Use the Coinbase symbol for SHIB
#
# # Order tracking
# orders = {'buy': [], 'sell': []}
# filled_buy_orders = []  # Track all filled buy orders
# filled_sell_orders = []  # Track all filled sell orders
# shib_owned = 0  # Track the amount of SHIB owned
#
#
# # Create grid levels
# def create_grid_levels(current_price):
#     grid_levels = {'buy': [], 'sell': []}
#
#     upper_limit = current_price * (1 + 0.1)
#     lower_limit = current_price * (1 - 0.1)
#
#     for i in range(1, num_grids + 1):
#         buy_price = current_price - (i * grid_size)
#         if buy_price >= lower_limit and buy_price > 0:
#             grid_levels['buy'].append(buy_price)
#
#     for i in range(1, num_grids + 1):
#         sell_price = current_price + (i * grid_size)
#         if sell_price <= upper_limit:
#             grid_levels['sell'].append(sell_price)
#
#     return grid_levels, upper_limit, lower_limit
#
#
# def get_current_price():
#     try:
#         return float(client.get_spot_price(currency_pair=symbol)['amount'])
#     except Exception as e:
#         print(f"Error fetching current price: {e}")
#         return None
#
#
# def place_orders(base_price):
#     global capital, shib_owned, total_profit
#     grid_levels, upper_limit, lower_limit = create_grid_levels(base_price)
#
#     for level in grid_levels['buy']:
#         if capital >= investment_amount:
#             amount_to_buy = investment_amount / level
#             if amount_to_buy > 0 and not any(order['price'] == level for order in filled_buy_orders):
#                 order_id = str(uuid.uuid4())  # Generate a unique ID
#                 orders['buy'].append({'id': order_id, 'price': level, 'amount': amount_to_buy})
#                 filled_buy_orders.append({'id': order_id, 'price': level, 'amount': amount_to_buy})
#                 capital -= investment_amount
#                 shib_owned += amount_to_buy
#     for buy_order in filled_buy_orders[:]:
#         buy_id, buy_price, amount_to_sell = buy_order['id'], buy_order['price'], buy_order['amount']
#         sell_level = next((lvl for lvl in grid_levels['sell'] if lvl > buy_price), None)
#
#         if sell_level and shib_owned >= amount_to_sell:
#             if not any(order['id'] == buy_id for order in filled_sell_orders):
#                 profit = (sell_level - buy_price) * amount_to_sell
#                 total_profit += profit  # Update total profit
#
#
#                 capital += sell_level * amount_to_sell
#                 shib_owned -= amount_to_sell
#                 orders['sell'].append({'id': buy_id, 'price': sell_level, 'amount': amount_to_sell})
#                 filled_sell_orders.append({'id': buy_id, 'price': sell_level, 'amount': amount_to_sell, 'profit': profit})
#                 # filled_buy_orders.remove(buy_order)
#
#
# def print_balance():
#     print("=" * 55)
#     print(f"Current portfolio balance: ${capital:.2f}")
#     print(f"Total SHIB owned: {shib_owned:.6f} SHIB")
#     print(f"Remaining Capital: {capital: .6f}")
#     current_price = get_current_price()
#     if current_price:
#         total_value = capital + (shib_owned * current_price)
#         print(f"Total portfolio value: ${total_value:.2f}")
#     print(f"Total profit since start: ${total_profit:.2f}")
#
#
# def display_filled_orders():
#     print("\n=== Filled Buy Orders ===")
#     for i, order in enumerate(filled_buy_orders, 1):
#         print(f"{i}. Bought {order['amount']:.6f} SHIB at ${order['price']:.8f}")
#
#     print("=" * 55)
#
#     print("\n=== Filled Sell Orders ===")
#     for i, order in enumerate(filled_sell_orders, 1):
#         print(f"{i}. Sold {order['amount']:.6f} SHIB at ${order['price']:.8f} | Profit: ${order['profit']:.2f}")
#
#     print("=" * 55)
#
#
# def monitor_orders():
#     cycle_count = 0
#     while True:
#         current_price = get_current_price()
#         if current_price is None:
#             time.sleep(3)
#             continue
#
#         print(f"Current market price: {current_price:.8f} USD")
#
#         if capital > 0:
#             print("Placing grid orders.")
#             place_orders(current_price)
#
#         print_balance()
#         display_filled_orders()
#
#         cycle_count += 1
#         if cycle_count % 20 == 0:
#             print("Refreshing grid levels based on the latest market price.")
#             place_orders(current_price)
#
#         time.sleep(4)
#
#
# if __name__ == "__main__":
#
#     print("Starting Paper Trading Grid Bot for SHIB with Real-Time Data")
#     initial_price = get_current_price()
#     if initial_price:
#         place_orders(initial_price)
#         monitor_orders()
#     else:
#         print("Failed to start bot due to issues fetching initial price.")


import os
import time
import uuid
from coinbase.wallet.client import Client

# Configuration parameters
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Initialize Coinbase client
client = Client(API_KEY, API_SECRET)

# Paper trading configuration
initial_capital = 200.00  # Total capital for paper trading
capital = initial_capital
total_profit = 0.00  # Track total profit since the start of the session
total_loss = 0.00
grid_size = 0.0000005  # Adjust this value based on market conditions
num_grids = 10  # Total number of buy/sell orders
investment_amount = 5.00  # Amount in USD per trade
symbol = 'SHIB-USD'  # Use the Coinbase symbol for SHIB

# Order tracking
orders = {'buy': [], 'sell': []}
filled_buy_orders = []  # Track all filled buy orders
filled_sell_orders = []  # Track all filled sell orders
shib_owned = 0  # Track the amount of SHIB owned


# Create grid levels
def create_grid_levels(current_price):
    grid_levels = {'buy': [], 'sell': []}

    upper_limit = current_price * (1 + 0.1)
    lower_limit = current_price * (1 - 0.1)

    for i in range(1, num_grids + 1):
        buy_price = current_price - (i * grid_size)
        if buy_price >= lower_limit and buy_price > 0:
            grid_levels['buy'].append(buy_price)

    for i in range(1, num_grids + 1):
        sell_price = current_price + (i * grid_size)
        if sell_price <= upper_limit:
            grid_levels['sell'].append(sell_price)

    return grid_levels, upper_limit, lower_limit


def get_current_price():
    try:
        return float(client.get_spot_price(currency_pair=symbol)['amount'])
    except Exception as e:
        print(f"Error fetching current price: {e}")
        return None


def place_orders(base_price):
    global capital, shib_owned, total_profit, total_loss
    grid_levels, upper_limit, lower_limit = create_grid_levels(base_price)

    # Place buy orders
    for level in grid_levels['buy']:
        if capital >= investment_amount:
            amount_to_buy = investment_amount / level
            if amount_to_buy > 0 and not any(order['price'] == level for order in filled_buy_orders):
                order_id = str(uuid.uuid4())  # Generate a unique ID
                orders['buy'].append({'id': order_id, 'price': level, 'amount': amount_to_buy})
                filled_buy_orders.append({'id': order_id, 'price': level, 'amount': amount_to_buy})
                capital -= investment_amount
                shib_owned += amount_to_buy

    # Place sell orders and calculate profit/loss
    for buy_order in filled_buy_orders[:]:
        buy_id, buy_price, amount_to_sell = buy_order['id'], buy_order['price'], buy_order['amount']
        sell_level = next((lvl for lvl in grid_levels['sell'] if lvl > buy_price), None)

        if sell_level and shib_owned >= amount_to_sell:
            if not any(order['id'] == buy_id for order in filled_sell_orders):
                profit = (sell_level - buy_price) * amount_to_sell
                total_profit += profit  # Update total profit

                if profit < 0:
                    print(f"Loss of ${abs(profit):.2f} on order {buy_id}")
                    total_loss += profit

                capital += sell_level * amount_to_sell
                shib_owned -= amount_to_sell
                orders['sell'].append({'id': buy_id, 'price': sell_level, 'amount': amount_to_sell})
                filled_sell_orders.append({'id': buy_id, 'price': sell_level, 'amount': amount_to_sell, 'profit': profit})


def print_balance():
    print("=" * 55)
    print(f"Current portfolio balance: ${capital:.2f}")
    print(f"Total SHIB owned: {shib_owned:.6f} SHIB")
    print(f"Remaining Capital: {capital:.6f}")
    current_price = get_current_price()
    if current_price:
        total_value = capital + (shib_owned * current_price)
        print(f"Total portfolio value: ${total_value:.2f}")
    print(f"Total profit since start: ${total_profit:.2f}")
    print(f"Total loss since start: ${total_loss:.2f}")


def display_filled_orders():
    print("\n=== Filled Buy Orders ===")
    for i, order in enumerate(filled_buy_orders, 1):
        print(f"{i}. Bought {order['amount']:.6f} SHIB at ${order['price']:.8f}")

    print("=" * 55)

    print("\n=== Filled Sell Orders ===")
    for i, order in enumerate(filled_sell_orders, 1):
        print(f"{i}. Sold {order['amount']:.6f} SHIB at ${order['price']:.8f} | Profit: ${order['profit']:.2f}")

    print("=" * 55)


def monitor_orders():
    cycle_count = 0
    while True:
        current_price = get_current_price()
        if current_price is None:
            time.sleep(3)
            continue

        print(f"Current market price: {current_price:.8f} USD")

        if capital > 0:
            print("Placing grid orders.")
            place_orders(current_price)

        print_balance()
        display_filled_orders()

        cycle_count += 1
        if cycle_count % 20 == 0:
            print("Refreshing grid levels based on the latest market price.")
            place_orders(current_price)

        time.sleep(4)


if __name__ == "__main__":
    print("Starting Paper Trading Grid Bot for SHIB with Real-Time Data")
    initial_price = get_current_price()
    if initial_price:
        place_orders(initial_price)
        monitor_orders()
    else:
        print("Failed to start bot due to issues fetching initial price.")
