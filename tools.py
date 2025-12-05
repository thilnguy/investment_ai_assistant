import datetime
from dotenv import load_dotenv
import os
import requests
import openai

load_dotenv()
GOLD_API_URL = "https://api.metalpriceapi.com/v1/latest"
GOLD_API_KEY = os.getenv("METAL_PRICE_API_KEY")
MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# Demo prices (realistic current gold prices as fallback)
recent_updated_prices = {
    'USD': 0, 'GBP': 0.0, 'EUR': 0.0, 'JPY': 0.0,
    'CAD': 0, 'AUD': 0.0, 'INR': 0.0, 'CNY': 0.0,
    'SAR': 0.0, 'AED': 0.0, 'EGP': 0.0, 'VND': 0.0
}

def generate_investment_advice(currency, price, country):
    raise NotImplementedError

def get_gold_price(country):
    """
    Get current gold price in a specific country.
    return gold price in country's currency.
    """
    
    # Currency mapping for different countries
    currency_map = {
        'usa': 'USD', 'united states': 'USD', 'us': 'USD',
        'uk': 'GBP', 'britain': 'GBP', 'england': 'GBP',
        'europe': 'EUR', 'germany': 'EUR', 'france': 'EUR',
        'japan': 'JPY', 'canada': 'CAD', 'australia': 'AUD',
        'india': 'INR', 'china': 'CNY', 'saudi arabia': 'SAR',
        'uae': 'AED', 'egypt': 'EGP',
        'vietnam': 'VND', 'vn': 'VND'
    }
    
    currency = currency_map.get(country.lower(), 'USD')
    api_success = False
    try:
        params = {
            "api_key":GOLD_API_KEY,
            'base': 'XAU',
            'symbols': currency
        }
        response = requests.get(GOLD_API_URL, params=params, timeout=10)
        
        print(f"Gold price API response status: {response.status_code}")
        if response.status_code != 200:
            print("API request failed.")
        
        data = response.json()
        print(f"Gold price API response: {data}")
        if 'rates' not in data or currency not in data['rates']:
            print("Error retrieving gold price data.")
        
        price = data['rates'][currency]
        if price < 0:
            print("Invalid gold price data received.")
        elif price == 0:
            # Use recent updated price if API returns zero
            print("API returned zero price, using recent updated price.")
            price = recent_updated_prices[currency]
        else:
            # Update recent updated price if valid price received
            price = round(price, 2)
            recent_updated_prices[currency] = price
            
        api_success = True
        
            
    except Exception as e:
        print (f"Error retrieving gold price: {e}")
        
    return {
        'currency': currency,
        'price': price,
        'country': country,
        'timestamp': datetime.datetime.now().isoformat(),
        'data_source': 'API' if api_success else 'recent_updated_prices',
    }
    

def get_risk_level_assessment(price, currency):
    """Risk assessment tool that determines price level and provides technical analysis"""
    
    # Currency-specific price thresholds (approximate)
    thresholds = {
        'USD': {'low': 2000, 'moderate': 2300, 'high': 2500},
        'EUR': {'low': 1850, 'moderate': 2150, 'high': 2350},
        'GBP': {'low': 1600, 'moderate': 1850, 'high': 2100},
        'JPY': {'low': 300000, 'moderate': 340000, 'high': 380000},
        'CAD': {'low': 2700, 'moderate': 3100, 'high': 3500},
        'AUD': {'low': 3000, 'moderate': 3500, 'high': 4000},
        'INR': {'low': 160000, 'moderate': 190000, 'high': 220000},
        'CNY': {'low': 14000, 'moderate': 16500, 'high': 19000},
        'SAR': {'low': 7500, 'moderate': 8500, 'high': 9500},
        'AED': {'low': 7300, 'moderate': 8300, 'high': 9300},
        'EGP': {'low': 95000, 'moderate': 110000, 'high': 125000}
    }
    
    # Get thresholds for currency or use USD as default
    thresh = thresholds.get(currency, thresholds['USD'])
    
    if price < thresh['low']:
        return {
            'risk_level': 'low',
            'price_classification': 'Undervalued',
            'advice': f"Excellent buying opportunity! Gold is undervalued at {price} {currency}. Consider accumulating positions while prices are low."
        }
    elif price < thresh['moderate']:
        return {
            'risk_level': 'moderate', 
            'price_classification': 'Fair Value',
            'advice': f"Good entry point at {price} {currency}. Moderate pricing with growth potential. Consider dollar-cost averaging for this market."
        }
    elif price < thresh['high']:
        return {
            'risk_level': 'moderate-high',
            'price_classification': 'Fairly Valued',
            'advice': f"Fair pricing at {price} {currency}. Market is fairly valued. Consider smaller purchases or wait for pullbacks."
        }
    else:
        return {
            'risk_level': 'high',
            'price_classification': 'Premium/Overvalued',
            'advice': f"Premium pricing at {price} {currency}. Consider waiting for market corrections or focus on smaller strategic purchases."
        }

    
def generate_gold_investment_advice(price, currency, country, history):
    """
    Get investment advice from the LLM based on chat history and investment type.
    """
    
    risk_analysis = get_risk_level_assessment(price, currency)
    risk_level = risk_analysis['risk_level']
    fallback_advice = risk_analysis['technical_analysis']
    
    system_prompt = f"""
    As a professional gold investment advisor, provide specific investment advice based on these current market conditions:
    
    MARKET DATA:
    - Current gold price: {price} {currency}
    - Country/Market: {country}
    - Currency: {currency}
    
    RISK ASSESSMENT TOOL OUTPUT:
    - Risk Level: {risk_level.upper()}
    - Price Classification: {risk_analysis['price_classification']}
    - Technical Analysis: {fallback_advice}
    
    Based on this risk assessment tool output, provide professional investment advice that:
    1. Acknowledges the {risk_level} risk level
    2. Provides specific timing recommendations
    3. Considers currency-specific factors for {currency}
    4. Offers actionable next steps
    
    Keep your advice concise (2-3 sentences), professional, and specific to the {risk_level} risk scenario.
    """
    messages = [{"role": "system", "content": system_prompt}] + history
    
    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    
    return response.choices[0].message.content
    
    