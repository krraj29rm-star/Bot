import os, threading, asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from aiohttp import web
import yfinance as yf
import pandas as pd
import numpy as np
TOKEN = os.environ.get("BOT_TOKEN")

def calc(entry):
    return round(entry*1.4, 1), round(entry*0.75, 1)

def live(sym):
    try:
        d = yf.Ticker(sym).history(period="5d")
        return float(d['Close'].iloc[-1]), float(d['High'].max()), float(d['Low'].min())
    except:
        return 0, 0, 0

def atm_strike(spot, step):
    return int(round(spot/step)*step)

async def start(u, c):
    await u.message.reply_text("🔥 BEST BOT READY!\n\n/nifty - NIFTY LIVE\n/sensex - SENSEX LIVE\n/stockoption - BEST STOCKS LIVE ATM\n/option - NIFTY OPTION LIVE\n/commodity - GOLD SILVER CRUDE\n/intraday - INTRADAY\n/swing - SWING\n/btst - BTST")

async def nifty_cmd(u, c):
    spot, ph, pl = live("^NSEI")
    await u.message.reply_text(f"🌞 NIFTY LIVE: {spot:.2f}\nHigh: {ph:.2f} Low: {pl:.2f}\nBuy Above: {ph:.2f} | Sell Below: {pl:.2f}")

async def sensex_cmd(u, c):
    spot, ph, pl = live("^BSESN")
    await u.message.reply_text(f"🌞 SENSEX LIVE: {spot:.2f}\nHigh: {ph:.2f} Low: {pl:.2f}")

async def intraday(u, c):
    await u.message.reply_text("Wait... LIVE edukuren...")
    spot, ph, pl = live("^NSEI")
    atm = atm_strike(spot, 50)
    await u.message.reply_text(f"📈 INTRADAY NIFTY: {spot:.2f}\nATM: {atm} CE - Buy Above {ph:.2f}\nTarget: {round(ph*1.005,1)} | SL: {round(pl,1)}")

async def swing(u, c):
    await u.message.reply_text("📈 SWING - RELIANCE / HDFC / INFY - /stockoption la paaru")

async def btst_cmd(u, c):
    spot, ph, pl = live("^NSEI")
    await u.message.reply_text(f"🌙 BTST NIFTY: {spot:.2f}\nTomorrow Buy Above: {ph:.2f}\nSL: {pl:.2f}")

async def stockoption(u, c):
    await u.message.reply_text("Wait... LIVE edukuren...")
    try:
        out = "📊 BEST STOCK OPTION - LIVE ATM\n\n"
        for name, sym, step in [("RELIANCE","RELIANCE.NS",10),("HDFC BANK","HDFCBANK.NS",10),("INFY","INFY.NS",10),("TCS","TCS.NS",10)]:
            spot, ph, pl = live(sym)
            atm = atm_strike(spot, step)
            est = round(spot*0.008, 1)
            t, s = calc(est)
            if spot > ph*0.99:
                sig = "BUY CE 🔥"
            elif spot < pl*1.01:
                sig = "BUY PE 🔥"
            else:
                sig = "WAIT"
            out += f"{name} Spot: {spot:.2f}\nATM: {atm} CE - {sig}\nEntry: {est}\nTarget: {t} | SL: {s}\n\n"
        await u.message.reply_text(out)
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")

async def option(u, c):
    await u.message.reply_text("Wait... NIFTY LIVE edukuren...")
    try:
        spot, ph, pl = live("^NSEI")
        atm = atm_strike(spot, 50)
        est = round(spot*0.005, 1)
        t, s = calc(est)
        if spot > ph*0.99:
            sig = f"BUY {atm} CE 🔥"
        else:
            sig = f"WAIT - {atm} CE ku mela close aana BUY"
        await u.message.reply_text(f"🔥 NIFTY LIVE: {spot:.2f}\nATM Strike: {atm}\n{sig}\nEntry: {est}\nTarget: {t} | SL: {s}\n\nExpiry Tomorrow - 3 PM ku munnadi exit!")
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")

async def commodity(u, c):
    await u.message.reply_text("Wait...")
    try:
        out = "🛢️ COMMODITY LIVE\n\n"
        for name, sym in [("GOLD","GC=F"),("SILVER","SI=F"),("CRUDE","CL=F")]:
            spot, ph, pl = live(sym)
            if spot > ph*0.99: sig = "BUY 🔥"
            elif spot < pl*1.01: sig = "SELL 🔥"
            else: sig = "WAIT"
            out += f"{name}: {spot:.2f} - {sig}\nBuy: {ph:.2f} | Sell: {pl:.2f}\n\n"
        await u.message.reply_text(out)
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")
async def commodityoption(u, c):
    await u.message.reply_text("Wait...")
    try:
        out = "🛢️ COMMODITY OPTION - LIVE ATM\n\n"
        for name, sym, gap in [("GOLD","GC=F",50),("SILVER","SI=F",1),("CRUDE","CL=F",1)]:
            spot, ph, pl = live(sym)
            atm = round(spot / gap) * gap
            side = "CE - BUY CE 🔥" if spot >= atm else "PE - BUY PE 🔥"
            entry = round(spot * 0.004, 1)
            target = round(entry * 1.4, 1)
            sl = round(entry * 0.75, 1)
            out += f"{name} Spot: {spot:.2f}\nATM: {atm} {side}\nEntry: {entry} | Target: {target} | SL: {sl}\n\n"
        await u.message.reply_text(out)
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")
        def rsi_calc(df, period=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def supertrend_calc(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    atr = (df['High'] - df['Low']).rolling(period).mean()
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    st = [True] * len(df)
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]:
            st[i] = True
        elif df['Close'].iloc[i] < lower.iloc[i-1]:
            st[i] = False
        else:
            st[i] = st[i-1]
    return st[-1], atr.iloc[-1]

def check_breakout(symbol, name):
    df15 = yf.download(symbol, period="5d", interval="15m", progress=False)
    df1h = yf.download(symbol, period="5d", interval="60m", progress=False)
    df15.columns = [c[0] if isinstance(c, tuple) else c for c in df15.columns]
    df1h.columns = [c[0] if isinstance(c, tuple) else c for c in df1h.columns]
    close = float(df15['Close'].iloc[-1])
    prev_high = float(df15['High'].iloc[-20:-1].max())
    prev_low = float(df15['Low'].iloc[-20:-1].min())
    prev_close = float(df15['Close'].iloc[-2])
    vwap = float(((df15['Close'] * df15['Volume']).sum() / df15['Volume'].sum()))
    vol = float(df15['Volume'].iloc[-1])
    avg_vol = float(df15['Volume'].iloc[-20:-1].mean())
    vol_high = vol > avg_vol
    r = float(rsi_calc(df15).iloc[-1])
    st15, atr = supertrend_calc(df15)
    st1h, _ = supertrend_calc(df1h)
    is_buy = close > prev_high
    is_sell = close < prev_low
    retest_buy = prev_close > prev_high or abs(close - prev_high) / prev_high < 0.002
    retest_sell = prev_close < prev_low or abs(close - prev_low) / prev_low < 0.002
    score_buy = sum([is_buy, retest_buy, r > 55, st15, vol_high, close > vwap, st1h])
    score_sell = sum([is_sell, retest_sell, r < 45, not st15, vol_high, close < vwap, not st1h])
    if score_buy == 7:
        return f"🟢 {name} - STRONG BUY (7/7)\nSpot: {close:.1f} | Break: {prev_high:.1f}\nRSI: {r:.0f} | ST: GREEN | VWAP: Mela | Vol: HIGH\nEntry: {close:.1f} | SL: {close-atr*1.5:.1f} | Target: {close+atr*2:.1f}\n\n"
    if score_sell == 7:
        return f"🔴 {name} - STRONG SELL (7/7)\nSpot: {close:.1f} | Break: {prev_low:.1f}\nRSI: {r:.0f} | ST: RED | VWAP: Keezha | Vol: HIGH\nEntry: {close:.1f} | SL: {close+atr*1.5:.1f} | Target: {close-atr*2:.1f}\n\n"
    return f"⚠️ {name} - WAIT ({max(score_buy, score_sell)}/7)\nSpot: {close:.1f} | RSI: {r:.0f}\n\n"

async def breakout_all(u, c):
    msg = "📊 BREAKOUT SCANNER (7 Confirm)\n\n"
    SYMBOLS = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "GOLD": "GC=F", "SILVER": "SI=F", "CRUDE": "CL=F"}
    for name, sym in SYMBOLS.items():
        try:
            msg += check_breakout(sym, name)
        except Exception as e:
            msg += f"⚪ {name} - Data illa\n\n"
    await u.message.reply_text(msg)
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('nifty', nifty_cmd))
app.add_handler(CommandHandler('sensex', sensex_cmd))
app.add_handler(CommandHandler('btst', btst_cmd))
app.add_handler(CommandHandler('intraday', intraday))
app.add_handler(CommandHandler('swing', swing))
app.add_handler(CommandHandler('option', option))
app.add_handler(CommandHandler('stockoption', stockoption))
app.add_handler(CommandHandler('stock', stockoption))
app.add_handler(CommandHandler("commodity", commodity))
app.add_handler(CommandHandler("commodityoption", commodityoption))
app.add_handler(CommandHandler("commodityoptions", commodityoption))
app.add_handler(CommandHandler("niftyoption", option))
app.add_handler(CommandHandler("breakout_all", breakout_all))
async def handle(request):
    return web.Response(text="Bot Live")

async def run_web():
    port = int(os.environ.get("PORT", 5000))
    a = web.Application()
    a.router.add_get("/", handle)
    runner = web.AppRunner(a)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    await asyncio.Event().wait()
def run_web_thread():
    asyncio.run(run_web())

threading.Thread(target=run_web_thread, daemon=True).start()
async def _run_bot():
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

asyncio.run(_run_bot())
