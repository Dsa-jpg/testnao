from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import time
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Načtení proměnných z .env souboru
load_dotenv()

# Nastavení API klíčů pomocí proměnných prostředí
api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

# Kontrola, zda byly API klíče načteny správně
if not api_key or not weather_api_key:
    raise ValueError("API klíče nebyly nalezeny. Ujistěte se, že jsou v souboru .env.")

client = OpenAI(api_key=api_key)

app = Flask(__name__)

# Proměnné pro ukládání časů
processing_times = []
delivery_times = []
openai_responses = []  # Ukládáme odpovědi od OpenAI API




@app.route('/openAI', methods=['GET', 'POST'])
def openAI():
    '''
    This method will handle the OpenAI API
    '''

    # Začneme měřit čas zpracování
    start_processing_time = time.time()

    # Přijmeme vstupní text z parametru "input_text"
    input_text = request.args.get('input_text', '')

    # Získáme aktuální datum a čas pro zahrnutí do zprávy pro robota
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Získání aktuálního počasí pro České Budějovice pomocí OpenWeatherMap API
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q=Ceske%20Budejovice&appid={weather_api_key}"
    response = requests.get(weather_url)
    weather_data = response.json()
    
    # Získání popisu počasí
    current_weather = weather_data["weather"][0]["description"]

    # Použijeme OpenAI API pro generování textu
    response = client.chat.completions.create(model="gpt-3.5-turbo-1106",
                                              messages=[
                                                  {
                                                      "role": "system",
                                                      "content": f"Jsi robot NAO. Je ti 14 let. A žiješ v Českých Budějovicích. Aktuální datum a čas: {current_datetime}. Aktuální počasí v Českých Budějovicích: {current_weather}. A nezmiňuj se o tom, že se jedná o požadavek HTTP POST, jen odpověz na otázku."
                                                  },
                                                  {
                                                      "role": "user",
                                                      "content": input_text,
                                                  }
                                              ])

    # Získáme generovaný text z OpenAI API odpovědi
    generated_text = response.choices[0].message.content
    openai_responses.append(generated_text)  # Uložíme odpověď

    # Skončíme měření času zpracování
    end_processing_time = time.time()
    processing_time = end_processing_time - start_processing_time
    processing_times.append(processing_time)

    # Začneme měřit čas doručení
    start_delivery_time = time.time()

    # Vrátíme generovaný text jako JSON odpověď
    response_json = {'generated_text': generated_text}

    # Skončíme měření času doručení
    end_delivery_time = time.time()
    delivery_time = end_delivery_time - start_delivery_time
    delivery_times.append(delivery_time)

    return jsonify(response_json)

@app.route('/stats')
def stats():
    '''
    Endpoint pro získání statistik
    '''
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0

    stats = {
        'avg_processing_time': avg_processing_time,
        'avg_delivery_time': avg_delivery_time,
        'total_requests': len(processing_times)
    }

    return render_template('stats.html', **stats, openai_responses=openai_responses)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 80))
