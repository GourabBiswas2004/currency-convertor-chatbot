from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

class CurrencyConverterBot:
    def __init__(self):
        self.api_key = "0ab4185b01e180a1bcc73e64"  # Replace with your API key
        self.base_url = "https://v6.exchangerate-api.com/v6/"
        self.rates = None
        self.last_base = None

    def get_exchange_rates(self, base_currency):
        try:
            if self.rates is None or self.last_base != base_currency:
                url = f"{self.base_url}{self.api_key}/latest/{base_currency}"
                response = requests.get(url)
                data = response.json()
                
                if data["result"] == "success":
                    self.rates = data["conversion_rates"]
                    self.last_base = base_currency
                    return self.rates
                return None
            return self.rates
        except:
            return None

    def convert_currency(self, amount, from_currency, to_currency):
        rates = self.get_exchange_rates(from_currency)
        
        if rates is None:
            return "Sorry, I couldn't fetch the exchange rates."
        
        if to_currency not in rates:
            return f"Invalid currency code: {to_currency}"
            
        converted_amount = amount * rates[to_currency]
        return f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}"

    def get_currency_list(self):
        if self.rates is None:
            self.get_exchange_rates("USD")
        if self.rates:
            return sorted(self.rates.keys())
        return []

# Initialize bot
bot = CurrencyConverterBot()

@app.route('/')
def index():
    currencies = bot.get_currency_list()
    return render_template('index.html', currencies=currencies)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    user_input = data.get('message', '').strip().lower()
    
    responses = {
        "hi bro": "Hello! How can I assist you today?",
        "hello": "Hi there! Need help with currency conversion?",
        "ok thank you": "you are most welcome",
        "would you like me": "chaal nikal yaha se",
        "how are you": "I'm just a bot, but I'm here to help! How about you?",
        "good morning": "Good morning! Ready to assist you with currency conversion.",
        "good night": "Good night! Sleep well!",
        "what is your name": "my name is gourab currency convertor, how can i help you!",
        "i need to convert currency": "Sure! Just type the amount and the currencies (e.g., 100 USD EUR).",
        "convert currency": "I can do that! Provide me with the amount and the currency pair (e.g., 50 GBP USD).",
        "can you convert currency": "Absolutely! Tell me the amount and the currencies you'd like to convert."  
    }
    
    if user_input in responses:
        return jsonify({'response': responses[user_input]})
    
    if user_input == 'list':
        currencies = bot.get_currency_list()
        return jsonify({'response': 'Available currencies: ' + ', '.join(currencies)})
    
    if user_input in ["thank you", "thanks"]:
        return jsonify({'response': "You're welcome! Happy to assist!"})
    
    if user_input in ["bye", "goodbye"]:
        return jsonify({'response': "Goodbye! Have a great day!"})
    
    if "tell me a joke" in user_input:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call fake spaghetti? An impasta!",
            "Why did the math book look sad? It had too many problems!",
            "Why are snails slow? Because they're carrying a house on their back."
        ]
        return jsonify({'response': random.choice(jokes)})
    
    if "exchange rate" in user_input or "rate of" in user_input:
        parts = user_input.split()
        if len(parts) == 3 and parts[0] == "rate":
            from_currency = parts[1].upper()
            to_currency = parts[2].upper()
            rates = bot.get_exchange_rates(from_currency)
            if rates and to_currency in rates:
                return jsonify({'response': f"1 {from_currency} = {rates[to_currency]:.2f} {to_currency}"})
            else:
                return jsonify({'response': f"Sorry, I couldn't fetch the exchange rate for {from_currency} to {to_currency}."})
        return jsonify({'response': "Format: rate from_currency to_currency (e.g., rate USD EUR)"})
    
    try:
        parts = user_input.split()
        if len(parts) != 3:
            return jsonify({'response': 'Format: amount from_currency to_currency (e.g., 100 USD EUR)'})
            
        amount = float(parts[0])
        from_currency = parts[1].upper()
        to_currency = parts[2].upper()
        
        result = bot.convert_currency(amount, from_currency, to_currency)
        short_messages = ["Got it!", "Here you go!", "Conversion done!", "Hope this helps!"]
        response_message = random.choice(short_messages) + " " + result
        
        return jsonify({'response': response_message})
        
    except ValueError:
        return jsonify({'response': 'Please enter a valid number for the amount'})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
