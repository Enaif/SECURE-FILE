import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URLs des tokens
urls = {
    'Base': 'https://basescan.org/token/0xD71552d9e08E5351AdB52163B3bbbC4d7DE53Ce1',
    'BSC': 'https://bscscan.com/token/0x2d060ef4d6bf7f9e5edde373ab735513c0e4f944',
    'Solana': 'https://api-v2.solscan.io/v2/token/holder/total'
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://google.com",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
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


# ---- UI Streamlit ----
st.set_page_config(page_title="AITECH Token Holders Tracker", page_icon="📊", layout="centered")

st.title("📊 AITECH Token Holders Tracker")

data = get_holders_data()
total = sum(val for val in data.values() if isinstance(val, int))

for chain, value in data.items():
    if isinstance(value, int):
        st.success(f"*{chain}*: {value}")
    else:
        st.error(f"*{chain}*: {value}")

st.markdown(f"### 🔢 Total holders across all chains: *{total}*")

