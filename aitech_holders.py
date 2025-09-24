# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 02:23:49 2025

@author: Soufiane.MOUMID
"""

from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# URLs des tokens
urls = {
    'Base': 'https://basescan.org/token/0xD71552d9e08E5351AdB52163B3bbbC4d7DE53Ce1',
    'BSC': 'https://bscscan.com/token/0x2d060ef4d6bf7f9e5edde373ab735513c0e4f944',
    'Solana': 'https://api-v2.solscan.io/v2/token/holder/total'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}


def get_holders_data():
    results = {}
    for chain, url in urls.items():
        try:
            if chain == 'Solana':
                params = {"address": "FUW4poh6s7uychceF8u1mo7NS65vzjX5vmS7Yi7GYQnz"}
                sol_headers = {
                    "accept": "application/json",
                    "origin": "https://solscan.io",
                    "referer": "https://solscan.io/",
                    "user-agent": headers['User-Agent']
                }
                response = requests.get(url, params=params, headers=sol_headers, verify=False)
                if response.ok:
                    data = response.json()
                    results[chain] = data.get("data")['holders']
                else:
                    results[chain] = "Error"
            else:
                response = requests.get(url, headers=headers, verify=False)
                if not response.ok:
                    results[chain] = "Error"
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                row = soup.find('div', id='ContentPlaceHolder1_tr_tokenHolders')
                div = row.find('div', class_='d-flex flex-wrap gap-2') if row else None
                if div:
                    count = int(div.text.strip().split()[0].replace(",", ""))
                    results[chain] = count
                else:
                    results[chain] = "Not found"
        except Exception as e:
            results[chain] = f"Error: {e}"
    return results


@app.route('/')
def index():
    data = get_holders_data()
    total = sum(val for val in data.values() if isinstance(val, int))

    html = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AITECH Token Holders Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Modern design with smooth shadows and rounded cards */
        body {
            margin: 0;
            padding: 40px;
            font-family: 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(to right, #f1f3f8, #e3e7ee);
            color: #2c3e50;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h1 {
            font-size: 32px;
            margin-bottom: 30px;
            color: #2d3436;
        }

        .card {
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            border-radius: 16px;
            padding: 20px 30px;
            margin: 10px 0;
            width: 100%;
            max-width: 400px;
            transition: transform 0.2s ease;
        }

        .card:hover {
            transform: translateY(-3px);
        }

        .success {
            border-left: 5px solid #27ae60;
        }

        .error {
            border-left: 5px solid #e74c3c;
        }

        .chain-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .chain-value {
            font-size: 18px;
        }

        .total {
            margin-top: 30px;
            font-size: 22px;
            font-weight: bold;
            color: #34495e;
        }

        @media (max-width: 480px) {
            body {
                padding: 20px;
            }

            h1 {
                font-size: 24px;
            }

            .card {
                padding: 15px 20px;
            }
        }
    </style>
</head>
<body>
    <h1>📊 AITECH Token Holders Tracker</h1>

    {% for chain, value in data.items() %}
        <div class="card {{ 'success' if value is number else 'error' }}">
            <div class="chain-title">{{ chain }}</div>
            <div class="chain-value">{{ value }}</div>
        </div>
    {% endfor %}

    <div class="total">🔢 Total holders across all chains: {{ total }}</div>
</body>
</html>

    '''

    def is_number(val):
        return isinstance(val, int)

    return render_template_string(html, data=data, total=total, is_number=is_number)

if __name__ == '_main_':
    app.run(debug=False)