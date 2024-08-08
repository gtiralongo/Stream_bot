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

# Definición de la función get_indicator_temp
def get_indicator_temp(symbolTicker, temp):
    dict_temp = {
        '1m': '|1',
        '5m': '|5',
        '15m': '|15',
        '30m': '|30',
        '1h': '|60',
        '4h': '|240',
        '1w': '|1W',
        '1M': '|1M'
    }
    temp_indicator = dict_temp.get(temp, '')
    indicator_list = [f'{indicator}{temp_indicator}' for indicator in data['indicators']]
    data = {
        'symbols': {'tickers': [f'BINANCE:{symbolTicker}']},
        'columns': indicator_list
    }
    headers = {'User-Agent': 'gustavo/2.0'}
    try:
        response = requests.post(URL, json=data, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"Error al cargar los indicadores: {e}")
    pre_result = response.json().get("data", [])
    oportunidad = {}
    for item in pre_result:
        symbol = item['s'][8:]
        result = item['d']
        oportunidad[symbol] = {indicator: result[idx] for idx, indicator in enumerate(data['indicators'])}
    return oportunidad

# Cargar datos
data = get_save_info('actions.json')

# Título de la aplicación
st.title('Dashboard de Bots de Trading')

# Obtener todos los símbolos únicos
symbols = list(set(bot_info['sym'] for bot_info in data['bot'].values()))

# Función para actualizar los precios cada minuto
@st.cache_data
def update_prices():
    current_prices = {}
    try:
        result = get_indicator_temp(','.join(symbols), ','.join(set(bot_info['graf_temp'] for bot_info in data['bot'].values())))
        for bot_name, bot_info in data['bot'].items():
            if bot_info['sym'] in result:
                current_prices[bot_info['sym']] = result[bot_info['sym']].get("close", 0)
            else:
                current_prices[bot_info['sym']] = 0
    except Exception as e:
        st.error(f"Error al obtener los precios actuales: {e}")
        current_prices = {symbol: 0 for symbol in symbols}
    return current_prices

# Función para crear la tabla de bots
def create_bots_table(current_prices):
    bots_data = []
    for bot_name, bot_info in data['bot'].items():
        current_price = current_prices.get(bot_info['sym'], 0)
        try:
            if bot_info['state'] == 'SELL':
                profit_loss = (current_price - float(bot_info['valor_compra'])) / float(bot_info['valor_compra']) * 100
                color = 'green' if current_price > float(bot_info['valor_compra']) else 'red'
            else:  # state == 'BUY'
                profit_loss = (float(bot_info['valor_venta']) - current_price) / current_price * 100
                color = 'red' if current_price > float(bot_info['valor_venta']) else 'green'
        except (ValueError, ZeroDivisionError):
            profit_loss = 0
            color = 'gray'
        
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
