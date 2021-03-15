from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
load_dotenv()
import os
import requests
app = Flask(__name__)

API_MANAGEMENT_URL = os.getenv("API_MANAGEMENT_URL")
LAGER_API_URL = os.getenv("LAGER_API_URL")

COGNITIVE_API_HEADER_KEY = 'Ocp-Apim-Subscription-Key'
COGNITIVE_API_HEADER_VAL = os.getenv("COGNITIVE_API_HEADER_VAL")

CONFIDENCE_THRESHOLD = 0.9

def get_stock_items():
    url = f'{LAGER_API_URL}/v2/products/everything'
    try: # Try/Except block in case the url doesn't work for some reason
        response = requests.get(url).json()
        if 'data' not in response:
            return None
        else:
            data = response['data']
            unique = {}
            for item in data:
                try: # The try/except block is a catch if the stock conversion to int goes wrong
                    name = item["name"].replace('"', '')
                    stock = int(item["stock"])
                    description = item["description"].replace('"', '')

                    if None in (name, stock, description, item["price"]):
                        continue

                    if name not in unique:
                        unique[name] = {
                            "name": name, 
                            "description": description, 
                            "stock": stock,
                            "price": item["price"]
                            }
                    else:
                        unique[name]["stock"] += stock
                except:
                    pass
            unique_lst = [ unique[key] for key in unique ]
            return unique_lst
    except:
        return None

def filter_items_by_words(stock, translations):
    filtered = []
    for item in stock:
        name = item['name']
        description = item['description']

        comparison = f'{name} {description}'
        if any([translation in comparison for translation in translations]):
            filtered.append(item)

    return filtered

def get_translations(from_lan, to_lan, items):
    try:
        url = f'{API_MANAGEMENT_URL}/translate?api-version=3.0&from={from_lan}&to={to_lan}'
        headers = { COGNITIVE_API_HEADER_KEY: COGNITIVE_API_HEADER_VAL }
        body = [
            {"text": item} for item in items
        ]
        response = requests.post(url, headers=headers, json=body).json()
        
        translations = []
        for item in response:
            for translation in item['translations']:
                translations.append(translation['text'])
        return translations
    except:
        return None

def get_cognitive_response(image_url):
    try:
        url = f'{API_MANAGEMENT_URL}/vision/v2.0/analyze?visualFeatures=Tags'
        headers = { COGNITIVE_API_HEADER_KEY: COGNITIVE_API_HEADER_VAL }
        body = { 'url': image_url }
        response = requests.post(url, headers=headers, json=body).json()

        if 'code' in response or 'statusCode' in response:
            return None, response['message']

        items = [
            item['name'] for item in response['tags'] if item['confidence'] > CONFIDENCE_THRESHOLD
        ]
        return items, ""
    except:
        return None, "API Management layer URL is invalid"
def get_relevant_products(image_url):
    NON_RELEVANT_SEARCH_TERMS_FAULT = "Could not find relevant search terms"

    # Image recognition with API Management layer by BTH
    items, cognitive_status = get_cognitive_response(image_url)
    if not items or len(items) == 0:
        return None, cognitive_status if cognitive_status else NON_RELEVANT_SEARCH_TERMS_FAULT

    # Translations with API Management layer by BTH
    translations = get_translations('en', 'sv', items)
    if not translations or len(translations) == 0:
        return None, NON_RELEVANT_SEARCH_TERMS_FAULT

    # Getting the stock from lager-api layer deployed by me
    stock = get_stock_items()
    if not stock:
        return None, "Could not find a database or the stock is empty"

    # Filter the stock by the translations
    items = filter_items_by_words(stock, translations)
    return items, ""

@app.route('/')
def home():
    return redirect('/image_search', code=302)

@app.route('/image_search')
def image_search():
    image_url = request.args.get("image-url", "")
    product_items, status = get_relevant_products(image_url)

    return render_template("index.html", image_url=image_url, items=product_items, currency="sek", status=status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)