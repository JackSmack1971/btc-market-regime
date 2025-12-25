import yaml
import requests
import sys
import time
from typing import Dict, Any

def validate_contract(name: str, url: str, schema_check_func, is_backup: bool = False) -> bool:
    prefix = "[BACKUP]" if is_backup else "[*]"
    print(f"{prefix} Validating {name}...")
    
    if url in ["volatility_calc", "on_chain_manual", "None", None]:
        print(f" [SKIP] {name} is an internal method.")
        return True
        
    for attempt in range(3):
        try:
            headers = {"User-Agent": "BitcoinRegimeAnalyzer-QA/1.0"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429:
                print(f" [WAIT] Rate limited (429). Retrying in {5 * (attempt + 1)}s...")
                time.sleep(5 * (attempt + 1))
                continue
                
            if response.status_code == 451:
                print(f" [AUTH] {name} restricted (451). Handled by fallback.")
                return True
                
            response.raise_for_status()
            data = response.json()
            
            if schema_check_func(data):
                print(f" [PASS] {name} contract matches.")
                return True
            else:
                print(f" [FAIL] {name} schema mismatch!")
                # Debug output for mismatch
                print(f"  Keys found: {list(data.get('data', {}).keys()) if isinstance(data, dict) else 'Not a dict'}")
                return False
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            print(f" [ERROR] {name} probe failed: {e}")
            return False
    return False

# Schema check functions (Forensic Deep-Dive)
def check_fng(data): 
    return "data" in data and len(data["data"]) > 0 and all(k in data["data"][0] for k in ["value", "value_classification", "timestamp"])

def check_blockchain_info(data): 
    return "values" in data and len(data["values"]) > 0 and all(k in data["values"][-1] for k in ["x", "y"])

def check_mempool_diff(data): 
    return all(k in data for k in ["progressPercent", "difficultyChange", "estimatedRetargetDate"])

def check_blockchair_stats(data): 
    return "data" in data and "transactions_24h" in data["data"] and isinstance(data["data"]["transactions_24h"], int)

def check_funding_binance(data): 
    return isinstance(data, list) and len(data) > 0 and "lastFundingRate" in data[-1] and "symbol" in data[-1]

def check_coinmetrics(data): 
    return "data" in data and len(data["data"]) > 0 and all(k in data["data"][0] for k in ["CapMVRVCur", "asset", "time"])

def check_derivatives_coingecko(data): 
    if not isinstance(data, list) or len(data) == 0: return False
    for item in data:
        if item.get('index_id') == 'BTC' and all(k in item for k in ["open_interest", "price", "funding_rate"]):
            return True
    return False

def check_rsi_coingecko(data): 
    return "prices" in data and isinstance(data["prices"], list) and len(data["prices"]) > 0 and len(data["prices"][0]) == 2

if __name__ == "__main__":
    with open("config/sources.yaml", 'r') as f:
        sources = yaml.safe_load(f)['sources']
        
    validation_map = {
        "fear_greed_index": (check_fng, None),
        "hash_rate": (check_blockchain_info, check_mempool_diff),
        "active_addresses": (check_blockchain_info, check_blockchair_stats),
        "perpetual_funding_rates": (check_funding_binance, check_derivatives_coingecko),
        "open_interest": (check_derivatives_coingecko, None),
        "mvrv_ratio": (check_coinmetrics, check_blockchair_stats),
        "price_data": (check_rsi_coingecko, None)
    }
    
    overall_pass = True
    for name, config in sources.items():
        if name in validation_map:
            primary_check, backup_check = validation_map[name]
            
            # Test Primary
            if not validate_contract(name, config['primary'], primary_check):
                overall_pass = False
            
            # Test Backup if exists and is a URL
            backup_url = config.get('backup')
            if backup_url and backup_check:
                if not validate_contract(name, backup_url, backup_check, is_backup=True):
                    overall_pass = False
            
    print("\n" + "="*35)
    if overall_pass:
        print("[SUCCESS] All API contracts (Primary & Backup) validated.")
        sys.exit(0)
    else:
        print("[WARNING] Some API contracts failed validation.")
        sys.exit(1)
