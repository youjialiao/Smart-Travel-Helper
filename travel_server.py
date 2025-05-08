from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# 國家和城市資料
COUNTRIES = {
    'Japan': {
        'cities': ['Tokyo', 'Osaka', 'Kyoto', 'Sapporo', 'Fukuoka'],
        'currency': 'JPY',
        'coordinates': {'Tokyo': {'lat': 35.6762, 'lon': 139.6503}, 
                        'Osaka': {'lat': 34.6937, 'lon': 135.5023}, 
                        'Kyoto': {'lat': 35.0116, 'lon': 135.7681},
                        'Sapporo': {'lat': 43.0621, 'lon': 141.3544},
                        'Fukuoka': {'lat': 33.5902, 'lon': 130.4017}},
        'info': {
            'language': '日語',
            'timezone': 'UTC+9',
            'plugType': 'A型、B型 (兩扁插頭)',
            'voltage': '100V',
            'emergencyNumber': '110 (警察) / 119 (救護/消防)'
        }
    },
    'Thailand': {
        'cities': ['Bangkok', 'Phuket', 'Chiang Mai', 'Pattaya'],
        'currency': 'THB',
        'coordinates': {'Bangkok': {'lat': 13.7563, 'lon': 100.5018}, 
                        'Phuket': {'lat': 7.8804, 'lon': 98.3923}, 
                        'Chiang Mai': {'lat': 18.7883, 'lon': 98.9853},
                        'Pattaya': {'lat': 12.9236, 'lon': 100.8825}},
        'info': {
            'language': '泰語',
            'timezone': 'UTC+7',
            'plugType': 'A型、B型、C型 (兩扁插頭/歐規圓頭)',
            'voltage': '220V',
            'emergencyNumber': '191 (警察) / 1669 (救護)'
        }
    },
    'France': {
        'cities': ['Paris', 'Nice', 'Lyon', 'Marseille'],
        'currency': 'EUR',
        'coordinates': {'Paris': {'lat': 48.8566, 'lon': 2.3522}, 
                        'Nice': {'lat': 43.7102, 'lon': 7.2620}, 
                        'Lyon': {'lat': 45.7640, 'lon': 4.8357},
                        'Marseille': {'lat': 43.2965, 'lon': 5.3698}},
        'info': {
            'language': '法語',
            'timezone': 'UTC+1 (夏令時UTC+2)',
            'plugType': 'C型、E型 (歐規圓頭)',
            'voltage': '230V',
            'emergencyNumber': '112 (通用) / 15 (救護)'
        }
    },
    'United States': {
        'cities': ['New York', 'Los Angeles', 'San Francisco', 'Chicago', 'Las Vegas'],
        'currency': 'USD',
        'coordinates': {'New York': {'lat': 40.7128, 'lon': -74.0060}, 
                        'Los Angeles': {'lat': 34.0522, 'lon': -118.2437}, 
                        'San Francisco': {'lat': 37.7749, 'lon': -122.4194},
                        'Chicago': {'lat': 41.8781, 'lon': -87.6298},
                        'Las Vegas': {'lat': 36.1699, 'lon': -115.1398}},
        'info': {
            'language': '英語',
            'timezone': '各時區不同，東岸UTC-5，西岸UTC-8',
            'plugType': 'A型、B型 (兩扁插頭)',
            'voltage': '120V',
            'emergencyNumber': '911 (通用)'
        }
    },
    'Australia': {
        'cities': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
        'currency': 'AUD',
        'coordinates': {'Sydney': {'lat': -33.8688, 'lon': 151.2093}, 
                        'Melbourne': {'lat': -37.8136, 'lon': 144.9631}, 
                        'Brisbane': {'lat': -27.4698, 'lon': 153.0251},
                        'Perth': {'lat': -31.9505, 'lon': 115.8605},
                        'Adelaide': {'lat': -34.9285, 'lon': 138.6007}},
        'info': {
            'language': '英語',
            'timezone': '各時區不同，東岸UTC+10',
            'plugType': 'I型 (三扁插頭)',
            'voltage': '230V',
            'emergencyNumber': '000 (通用)'
        }
    }
}

# 天氣代碼映射
WEATHER_CODES = {
    0: '晴天',
    1: '晴時多雲',
    2: '多雲',
    3: '陰天',
    45: '霧',
    48: '霧凇',
    51: '毛毛雨',
    53: '小雨',
    55: '中雨',
    56: '凍雨',
    57: '強凍雨',
    61: '小雨',
    63: '中雨',
    65: '大雨',
    66: '凍雨',
    67: '強凍雨',
    71: '小雪',
    73: '中雪',
    75: '大雪',
    77: '雪粒',
    80: '陣雨',
    81: '強陣雨',
    82: '暴雨',
    85: '小雪',
    86: '大雪',
    95: '雷雨',
    96: '雷雨伴有冰雹',
    99: '強雷雨伴有冰雹'
}

@app.route('/')
def index():
    return render_template('index.html', countries=COUNTRIES)

@app.route('/api/countries', methods=['GET'])
def get_countries():
    return jsonify(list(COUNTRIES.keys()))

@app.route('/api/cities', methods=['GET'])
def get_cities():
    country = request.args.get('country')
    if country in COUNTRIES:
        return jsonify(COUNTRIES[country]['cities'])
    return jsonify([])

@app.route('/api/country_info', methods=['GET'])
def get_country_info():
    country = request.args.get('country')
    if country in COUNTRIES:
        return jsonify(COUNTRIES[country]['info'])
    return jsonify({})

@app.route('/api/exchange_rate', methods=['GET'])
def get_exchange_rate():
    country = request.args.get('country')
    
    if country not in COUNTRIES:
        return jsonify({'error': '無效的國家'}), 400
    
    currency = COUNTRIES[country]['currency']
    
    try:
        # 使用open.er-api.com取得匯率資料
        response = requests.get(f'https://open.er-api.com/v6/latest/TWD')
        data = response.json()
        
        if 'rates' in data and currency in data['rates']:
            return jsonify({
                'base': 'TWD',
                'target': currency,
                'rate': data['rates'][currency],
                'last_updated': data.get('time_last_updated', '')
            })
        else:
            return jsonify({'error': '無法獲取匯率資料'}), 500
            
    except Exception as e:
        print(f"匯率API錯誤: {str(e)}")
        return jsonify({'error': '取得匯率資料時發生錯誤'}), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """獲取當前天氣資訊"""
    country = request.args.get('country')
    city = request.args.get('city')
    
    if country not in COUNTRIES:
        return jsonify({'error': '無效的國家'}), 400
        
    if city not in COUNTRIES[country]['cities']:
        return jsonify({'error': '無效的城市'}), 400
    
    coordinates = COUNTRIES[country]['coordinates'].get(city)
    if not coordinates:
        return jsonify({'error': '找不到該城市的座標資料'}), 400
    
    try:
        # 使用Open-Meteo API取得天氣資料
        lat = coordinates['lat']
        lon = coordinates['lon']
        
        response = requests.get(
            f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code'
        )
        data = response.json()
        
        if 'current' in data:
            current = data['current']
            weather_code = current.get('weather_code')
            weather_description = WEATHER_CODES.get(weather_code, '未知')
            
            return jsonify({
                'city': city,
                'country': country,
                'temperature': current.get('temperature_2m'),
                'weather_code': weather_code,
                'weather': weather_description
            })
        else:
            return jsonify({'error': '無法獲取天氣資料'}), 500
            
    except Exception as e:
        print(f"天氣API錯誤: {str(e)}")
        return jsonify({'error': '取得天氣資料時發生錯誤'}), 500

@app.route('/api/weather/weekly', methods=['GET'])
def get_weekly_weather():
    """獲取一周天氣預報"""
    country = request.args.get('country')
    city = request.args.get('city')
    
    if country not in COUNTRIES:
        return jsonify({'error': '無效的國家'}), 400
        
    if city not in COUNTRIES[country]['cities']:
        return jsonify({'error': '無效的城市'}), 400
    
    coordinates = COUNTRIES[country]['coordinates'].get(city)
    if not coordinates:
        return jsonify({'error': '找不到該城市的座標資料'}), 400
    
    try:
        # 使用Open-Meteo API取得一周天氣預報資料
        lat = coordinates['lat']
        lon = coordinates['lon']
        
        response = requests.get(
            f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&timezone=auto'
        )
        data = response.json()
        
        if 'daily' in data:
            daily = data['daily']
            days = len(daily.get('time', []))
            
            forecast = []
            for i in range(days):
                date = daily['time'][i]
                weather_code = daily['weather_code'][i]
                weather_description = WEATHER_CODES.get(weather_code, '未知')
                
                day_data = {
                    'date': date,
                    'max_temp': daily['temperature_2m_max'][i],
                    'min_temp': daily['temperature_2m_min'][i],
                    'weather_code': weather_code,
                    'weather': weather_description,
                    'precipitation': daily['precipitation_sum'][i],
                    'precipitation_probability': daily['precipitation_probability_max'][i]
                }
                forecast.append(day_data)
            
            return jsonify({
                'city': city,
                'country': country,
                'forecast': forecast,
                'units': {
                    'temperature': data.get('daily_units', {}).get('temperature_2m_max', '°C'),
                    'precipitation': data.get('daily_units', {}).get('precipitation_sum', 'mm')
                }
            })
        else:
            return jsonify({'error': '無法獲取一周天氣預報資料'}), 500
            
    except Exception as e:
        print(f"一周天氣預報API錯誤: {str(e)}")
        return jsonify({'error': '取得一周天氣預報資料時發生錯誤'}), 500

@app.route('/api/convert_currency', methods=['GET'])
def convert_currency():
    country = request.args.get('country')
    amount = request.args.get('amount', type=float)
    from_currency = request.args.get('from')  # 'TWD' or target currency
    
    if country not in COUNTRIES:
        return jsonify({'error': '無效的國家'}), 400
        
    if amount is None:
        return jsonify({'error': '無效的金額'}), 400
    
    currency = COUNTRIES[country]['currency']
    
    try:
        # 獲取匯率
        response = requests.get(f'https://open.er-api.com/v6/latest/TWD')
        data = response.json()
        
        if 'rates' in data and currency in data['rates']:
            rate = data['rates'][currency]
            
            # 計算轉換後的金額
            if from_currency == 'TWD':
                # TWD -> 外幣
                converted_amount = amount * rate
                to_currency = currency
            else:
                # 外幣 -> TWD
                converted_amount = amount / rate
                to_currency = 'TWD'
            
            return jsonify({
                'from': from_currency,
                'to': to_currency,
                'amount': amount,
                'converted_amount': round(converted_amount, 2),
                'rate': rate
            })
        else:
            return jsonify({'error': '無法獲取匯率資料'}), 500
            
    except Exception as e:
        print(f"貨幣轉換錯誤: {str(e)}")
        return jsonify({'error': '轉換貨幣時發生錯誤'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)