import streamlit as st
import json
import pandas as pd
import requests
import time

def save_info(info, file):
    with open(file, 'r') as fp:
        data = json.load(fp)
    data.update(info)
    with open(file, 'w') as fp:
        json.dump(data, fp)
    fp.close()

@st.cache_data
def get_save_info(file):
    with open(file, 'r') as fp:
        data = json.load(fp)
    fp.close()
    return data

# Función para obtener los precios actuales de todos los símbolos
def get_current_prices(symbols, indicators, timeframes):
    URL = "https://scanner.tradingview.com/crypto/scan"
    exchange = 'BINANCE'
    payload = {
        "filter": {
            "symbols": {
                "query": {
                    "types": [
                        "crypto"
                    ]
                },
                "tickers": symbols
            },
            "indicators": indicators,
            "timeframe": timeframes
        },
        "columns": [
            "close",
            "open",
            "high",
            "low",
            "volume",
            "change"
        ],
        "range": {
            "from": time.time() - 60,  # Últimos 60 segundos
            "to": time.time()
        }
    }
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'data' in data:
            current_prices = {item['ticker']: float(item['close']) for item in data['data']}
        else:
            current_prices = {symbol: 0 for symbol in symbols}
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener los precios actuales: {e}")
        current_prices = {symbol: 0 for symbol in symbols}
    return current_prices

# Cargar datos
data = get_save_info('actions.json')

# Título de la aplicación
st.title('Dashboard de Bots de Trading')

# Obtener todos los símbolos únicos
symbols = list(set(bot_info['sym'] for bot_info in data['bot'].values()))

# Obtener los indicadores y temporalidades únicos
indicators = list(set(data['indicators']))
timeframes = list(set(bot_info['graf_temp'] for bot_info in data['bot'].values()))

# Función para actualizar los precios cada minuto
@st.cache_data
def update_prices():
    current_prices = get_current_prices(symbols, indicators, ','.join(timeframes))
    return current_prices

# Función para crear la tabla de bots
def create_bots_table(current_prices):
    bots_data = []
    for bot_name, bot_info in data['bot'].items():
        current_price = current_prices.get(bot_info['sym'], 0)
        if bot_info['state'] == 'SELL':
            profit_loss = (current_price - float(bot_info['valor_compra'])) / float(bot_info['valor_compra']) * 100
            color = 'green' if current_price > float(bot_info['valor_compra']) else 'red'
        else:  # state == 'BUY'
            profit_loss = (float(bot_info['valor_venta']) - current_price) / current_price * 100
            color = 'red' if current_price > float(bot_info['valor_venta']) else 'green'
        
        bots_data.append({
            'Bot': bot_name,
            'Símbolo': bot_info['sym'],
            'Estado': bot_info['state'],
            'Precio Actual': current_price,
            'Precio Compra': bot_info['valor_compra'],
            'Precio Venta': bot_info['valor_venta'],
            'Ganancia/Pérdida (%)': round(profit_loss, 2),
            'Color': color
        })
    
    df_bots = pd.DataFrame(bots_data)
    return df_bots

# Actualizar la tabla de bots cada minuto
while True:
    try:
        current_prices = update_prices()
        df_bots = create_bots_table(current_prices)
        st.subheader('Resumen de Bots')
        st.dataframe(df_bots.style.apply(lambda x: ['background-color: ' + x['Color']] * len(x), axis=1))
    except Exception as e:
        st.error(f"Error al actualizar la tabla de bots: {e}")
    time.sleep(60)
