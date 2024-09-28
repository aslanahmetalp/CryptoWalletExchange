import requests

class Wallet:
    def __init__(self, currency, balance=0):
        self.currency = currency
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited {amount} {self.currency}. New balance: {self.balance} {self.currency}")

    def withdraw(self, amount):
        if amount > self.balance:
            print(f"Insufficient balance to withdraw {amount} {self.currency}")
            return False
        self.balance -= amount
        print(f"Withdrew {amount} {self.currency}. New balance: {self.balance} {self.currency}")
        return True

class Exchange:
    def __init__(self):
        self.rates = {
            ('BTC', 'ETH'): 0.03,
            ('ETH', 'BTC'): 33.33,
            ('BTC', 'USD'): 50000,
            ('USD', 'BTC'): 0.00002,
            ('ETH', 'USD'): 4000,
            ('USD', 'ETH'): 0.00025
        }

    def update_rates_from_api(self):
        try:
            # Get BTC, ETH and USD rates from CoinGecko API
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,eth"
            response = requests.get(url)
            data = response.json()

            # Processing data from API
            btc_usd = data['bitcoin']['usd']
            eth_usd = data['ethereum']['usd']
            btc_eth = data['bitcoin']['eth']
            eth_btc = 1 / btc_eth  # ETH'den BTC'ye oran

            # update rates
            self.rates[('BTC', 'USD')] = btc_usd
            self.rates[('USD', 'BTC')] = 1 / btc_usd
            self.rates[('ETH', 'USD')] = eth_usd
            self.rates[('USD', 'ETH')] = 1 / eth_usd
            self.rates[('BTC', 'ETH')] = btc_eth
            self.rates[('ETH', 'BTC')] = eth_btc

            print("Exchange rates updated successfully from API.")

        except Exception as e:
            print(f"Error while fetching exchange rates: {e}")

    def convert(self, from_wallet, to_wallet, amount):
        pair = (from_wallet.currency, to_wallet.currency)
        if pair not in self.rates:
            print(f"Exchange rate for {from_wallet.currency} to {to_wallet.currency} not available.")
            return False
        rate = self.rates[pair]
        converted_amount = amount * rate
        if from_wallet.withdraw(amount):
            to_wallet.deposit(converted_amount)
            print(f"Converted {amount} {from_wallet.currency} to {converted_amount} {to_wallet.currency}")
            return True
        return False

# Example usage
btc_wallet = Wallet('BTC', 1)
eth_wallet = Wallet('ETH', 10)
usd_wallet = Wallet('USD', 10000)

exchange = Exchange()

# Update rates from API
exchange.update_rates_from_api()

# Convert 0.1 BTC to ETH
exchange.convert(btc_wallet, eth_wallet, 0.1)

# Convert 5000 USD to BTC
exchange.convert(usd_wallet, btc_wallet, 5000)
