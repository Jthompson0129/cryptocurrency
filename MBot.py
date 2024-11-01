import os
import csv
import time
import uuid
from datetime import datetime, timedelta
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
investment_amount = 20.00  # Amount in USD per trade
symbol = 'SHIB-USD'  # Use the Coinbase symbol for SHIB

# Order tracking
orders = {'buy': [], 'sell': []}
filled_buy_orders = []  # Track all filled buy orders
filled_sell_orders = []  # Track all filled sell orders
shib_owned = 0  # Track the amount of SHIB
completed_orders = 0

today_date = datetime.now().strftime("%m-%d-%y")

# Add the date to the CSV file name
csv_file = f"filled_orders_{today_date}.csv"


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


trade_window_end = datetime.now() + timedelta(minutes=10)


def place_orders(base_price):
    global capital, shib_owned, total_profit, total_loss, completed_orders
    grid_levels, upper_limit, lower_limit = create_grid_levels(base_price)

    if datetime.now() < trade_window_end:
        print('trading window end time: ', trade_window_end)
        # Place buy orders
        for level in grid_levels['buy']:
            if capital >= investment_amount:
                amount_to_buy = investment_amount / level
                if amount_to_buy > 0 and not any(order['price'] == level for order in filled_buy_orders):
                    order_id = str(uuid.uuid4())  # Generate a unique ID
                    # Update timestamp each time a buy order is placed
                    current_time = datetime.now().strftime("%I:%M:%S.%f %p")[:-3]
                    orders['buy'].append({'id': order_id, 'price': level, 'amount': amount_to_buy})
                    filled_buy_orders.append(
                        {'id': order_id, 'price': level, 'amount': amount_to_buy, 'timestamp': current_time})
                    capital -= investment_amount
                    shib_owned += amount_to_buy

        for buy_order in filled_buy_orders[:]:
            buy_id, buy_price, amount_to_sell = buy_order['id'], buy_order['price'], buy_order['amount']
            sell_level = next((lvl for lvl in grid_levels['sell'] if lvl > buy_price), None)

            if sell_level and shib_owned >= amount_to_sell:
                if not any(order['id'] == buy_id for order in filled_sell_orders):
                    profit = (sell_level - buy_price) * amount_to_sell
                    total_profit += profit  # Update total profit
                    current_time = datetime.now().strftime("%I:%M:%S.%f %p")[:-3]  # Update timestamp for sell orders

                    if profit < 0:
                        print(f"Loss of ${abs(profit):.2f} on order {buy_id}")
                        total_loss += profit

                    completed_orders += 1
                    capital += sell_level * amount_to_sell
                    shib_owned -= amount_to_sell
                    orders['sell'].append({'id': buy_id, 'price': sell_level, 'amount': amount_to_sell})
                    filled_sell_orders.append(
                        {'id': buy_id, 'price': sell_level, 'amount': amount_to_sell, 'profit': profit,
                         'timestamp': current_time})
    else:
        # Place sell orders and calculate profit/loss
        print('trading window closed')
        for buy_order in filled_buy_orders[:]:
            buy_id, buy_price, amount_to_sell = buy_order['id'], buy_order['price'], buy_order['amount']
            sell_level = next((lvl for lvl in reversed(grid_levels['sell']) if lvl > buy_price), None)

            print("sell_level: ", sell_level)
            print("current price: ", get_current_price())
            if sell_level and shib_owned >= amount_to_sell:
                if not any(order['id'] == buy_id for order in filled_sell_orders):
                    profit = (sell_level - buy_price) * amount_to_sell
                    total_profit += profit  # Update total profit
                    current_time = datetime.now().strftime("%I:%M:%S.%f %p")[:-3]  # Update timestamp for sell orders

                    if profit < 0:
                        print(f"Loss of ${abs(profit):.2f} on order {buy_id}")
                        total_loss += profit

                    capital += sell_level * amount_to_sell
                    shib_owned -= amount_to_sell
                    orders['sell'].append({'id': buy_id, 'price': sell_level, 'amount': amount_to_sell})
                    filled_sell_orders.append(
                        {'id': buy_id, 'price': sell_level, 'amount': amount_to_sell, 'profit': profit,
                         'timestamp': current_time})

        if shib_owned == 0:
            print('Trade window closed. All SHIB sold. Exiting.\n')
            print_balance()
            exit()


def print_balance():
    print(f"Completed Buy/Sell orders: {completed_orders}")
    print(f"Current portfolio balance: ${capital:.2f}")
    print(f"Total SHIB left to sell: {shib_owned:.6f}")
    print(f"Total profit since start: ${total_profit:.2f}")
    print(f"Total loss since start: ${total_loss:.2f}")
    print("=" * 85, '\n')


# Ensure the CSV file has headers if it doesn't exist
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="") as file:
        headerWriter = csv.writer(file)
        headerWriter.writerow(["Order Type", "ID", "Price", "Amount", "Profit", "Timestamp"])


def display_filled_orders():
    # Load existing order IDs from CSV to avoid duplicates
    existing_order_ids = set()
    try:
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                # Assume order ID is the second column
                existing_order_ids.add(row[1])
    except FileNotFoundError:
        # File doesn't exist yet, so no existing orders
        pass

    # Write all filled buy and sell orders to CSV file, avoiding duplicates
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Combine buy and sell orders into one list
        all_orders = [
                         {"type": "Buy", **order} for order in filled_buy_orders if
                         order['id'] not in existing_order_ids
                     ] + [
                         {"type": "Sell", **order} for order in filled_sell_orders if
                         order['id'] not in existing_order_ids
                     ]

        # Sort combined orders by 'id' to maintain sequence
        all_orders.sort(key=lambda x: x['id'])

        # Write each order to the CSV file in sequence
        for order in all_orders:
            if order["type"] == "Buy":
                writer.writerow(["Buy", order['id'], f"{order['price']:.8f}", order['amount'], '', order['timestamp']])
            elif order["type"] == "Sell":
                writer.writerow(
                    ["Sell", order['id'], f"{order['price']:.8f}", order['amount'], f"{order['profit']:.8f}",
                     order['timestamp']])

    # Display only the last 10 buy orders
    print("\n=== Last 10 Filled Buy Orders ===")
    for i, order in enumerate(filled_buy_orders[-10:], 1):
        print(f"{i}. Bought {order['amount']:.6f} SHIB at ${order['price']:.8f} - Time: {order['timestamp']}")

    print("=" * 85)

    # Display only the last 10 sell orders
    print("\n=== Last 10 Filled Sell Orders ===")
    for i, order in enumerate(filled_sell_orders[-10:], 1):
        print(
            f"{i}. Sold {order['amount']:.6f} SHIB at ${order['price']:.8f} | Profit: ${order['profit']:.2f} - Time: {order['timestamp']}")

    print("=" * 85, "\n")


def monitor_orders():
    cycle_count = 0
    while True:
        current_price = get_current_price()
        if current_price is None:
            time.sleep(3)
            continue

        print(f"Current market price: {current_price:.8f} USD")

        if capital > 0:
            place_orders(current_price)

        display_filled_orders()
        print_balance()

        cycle_count += 1
        if cycle_count % 10 == 0:
            print("*" * 75)
            print("Refreshing grid levels based on the latest market price.")
            print("*" * 75)
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
