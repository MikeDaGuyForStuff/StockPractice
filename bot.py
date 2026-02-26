import ccxt
import time
import sqlite3
import os

# --- CONFIGURATION ---
SYMBOL = 'BTC/USDT'
STOP_LOSS_PCT = 0.005  # 0.5%
# Use the Fly.io volume path if it exists, otherwise use local path
DB_PATH = "/data/trading_data.db" if os.path.exists("/data") else "trading_data.db"

exchange = ccxt.binanceus({'enableRateLimit': True})

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (timestamp DATETIME, type TEXT, price REAL, profit REAL)''')
    conn.commit()
    conn.close()

def log_trade(t_type, price, profit=0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO trades VALUES (datetime('now'), ?, ?, ?)", (t_type, price, profit))
    conn.commit()
    conn.close()

def get_1m_high():
    # Fetch 2 candles (last minute and current)
    ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe='1m', limit=2)
    return ohlcv[0][2] # Index 2 is the 'High'

def run_bot():
    init_db()
    in_pos, entry_p, trail_stop = False, 0, 0
    print(f"Bot started. Monitoring {SYMBOL}...")
    
    while True:
        try:
            ticker = exchange.fetch_ticker(SYMBOL)
            curr_p = ticker['last']
            
            if not in_pos:
                high_target = get_1m_high()
                if curr_p > high_target:
                    in_pos, entry_p = True, curr_p
                    trail_stop = entry_p * (1 - STOP_LOSS_PCT)
                    log_trade('BUY', entry_p)
                    print(f"🚀 BUY at {entry_p}")
            else:
                # Update Trailing Stop Loss
                if curr_p * (1 - STOP_LOSS_PCT) > trail_stop:
                    trail_stop = curr_p * (1 - STOP_LOSS_PCT)
                
                # Check for Exit
                if curr_p < trail_stop:
                    profit = ((curr_p - entry_p) / entry_p) * 100
                    log_trade('SELL', curr_p, profit)
                    in_pos = False
                    print(f"💰 SELL at {curr_p} | Profit: {profit:.2f}%")

            time.sleep(5) # Check every 5 seconds
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()