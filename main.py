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
def get_fno_signal_5confirm(symbol, name, strike_step):
    df = yf.download(symbol, period="2d", interval="5m", progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.dropna()
    daily = yf.download(symbol, period="5d", interval="1d", progress=False)
    daily.columns = [c[0] if isinstance(c, tuple) else c for c in daily.columns]
    prev_high = float(daily['High'].iloc[-2])
    prev_low = float(daily['Low'].iloc[-2])
    live = float(df['Close'].iloc[-1])
    rsi = float(rsi_calc(df).iloc[-1])
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    vwap = float(df['VWAP'].iloc[-1])
    avg_vol = float(df['Volume'].tail(20).mean())
    curr_vol = float(df['Volume'].iloc[-1])
    atm = round(live / strike_step) * strike_step
    if live > prev_high:
        score = 0
        if curr_vol > avg_vol:
            score = score + 1
        if rsi > 55:
            score = score + 1
        if live > vwap:
            score = score + 1
        if df['Close'].iloc[-1] > prev_high:
            score = score + 1
        if df['Close'].iloc[-2] > prev_high:
            score = score + 1
        if score == 5:
            return "CONFIRMED BUY CE " + name + " " + str(atm)
        return "Breakout Vandhuchu Score " + str(score) + "/5 Wait " + name
    if live < prev_low:
        score = 0
        if curr_vol > avg_vol:
            score = score + 1
        if rsi < 45:
            score = score + 1
        if live < vwap:
            score = score + 1
        if df['Close'].iloc[-1] < prev_low:
            score = score + 1
        if df['Close'].iloc[-2] < prev_low:
            score = score + 1
        if score == 5:
            return "CONFIRMED BUY PE " + name + " " + str(atm)
        return "Breakdown Vandhuchu Score " + str(score) + "/5 Wait " + name
    return "No Trade " + name + " Live " + str(int(live)) + " Buy Above " + str(int(prev_high))
    
