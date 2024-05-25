import json
import time
import requests
from config import RPC, PUB_KEY, client
from solana.transaction import Signature
from solders.pubkey import Pubkey #type: ignore
from spl.token.instructions import get_associated_token_address
    
def find_data(data, field):
    if isinstance(data, dict):
        if field in data:
            return data[field]
        else:
            for value in data.values():
                result = find_data(value, field)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_data(item, field)
            if result is not None:
                return result
    return None

def get_token_balance(base_mint: str):
    try:

        headers = {"accept": "application/json", "content-type": "application/json"}

        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "getTokenAccountsByOwner",
            "params": [
                PUB_KEY,
                {"mint": base_mint},
                {"encoding": "jsonParsed"},
            ],
        }
        
        response = requests.post(RPC, json=payload, headers=headers)
        ui_amount = find_data(response.json(), "uiAmount")
        return float(ui_amount)
    except Exception as e:
        return None

def confirm_txn(txn_sig, max_retries=20, retry_interval=3):
    retries = 0
    if isinstance(txn_sig, str):
        txn_sig = Signature.from_string(txn_sig)
    while retries < max_retries:
        try:
            txn_res = client.get_transaction(txn_sig, encoding="json", commitment="confirmed", max_supported_transaction_version=0)
            txn_json = json.loads(txn_res.value.transaction.meta.to_json())
            if txn_json['err'] is None:
                print("Transaction confirmed... try count:", retries+1)
                return True
            print("Error: Transaction not confirmed. Retrying...")
            if txn_json['err']:
                print("Transaction failed.")
                return False
        except Exception as e:
            print("Awaiting confirmation... try count:", retries+1)
            retries += 1
            time.sleep(retry_interval)
    print("Max retries reached. Transaction confirmation failed.")
    return None

def get_token_data(token_address):
    url = "https://degen.fund/api/tokens"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=1",
        "TE": "trailers"
    }
    
    params = {'search': token_address}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()['tokens']
        return data
    else:
        print(f"Request failed with status code {response.status_code}")
        return None

def get_bonding_curve_accounts(mint: str):
    try:
        curve_state = get_token_data(mint)[0]['bondingCurve']
        curve_state = Pubkey.from_string(curve_state)
        mint = Pubkey.from_string(mint)
        curve_mint_ata = get_associated_token_address(curve_state, mint)
        return (curve_state, curve_mint_ata)
    except:
        return None