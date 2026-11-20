import os, threading, asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from aiohttp import web
import yfinance as yf
import pandas as pd
import numpy as np
TOKEN = os.environ.get("BOT_TOKEN")

CONFIG = {
    "GOLD": {"sym": "GC=F", "step": 10, "prem": 0.004},
    "SILVER": {"sym": "SI=F", "step": 0.5, "prem": 0.004},
    "CRUDE": {"sym": "CL=F", "step": 1, "prem": 0.004},
    "NATGAS": {"sym": "NG=F", "step": 0.25, "prem": 0.02},
}

def calc(entry):
    dec = 2 if entry < 5 else 1
    target = round(entry * 1.4, dec)
    sl = round(entry * 0.75, dec)
    if sl >= entry:
        sl = round(entry * 0.70, dec)
    return target, sl

def live(sym):
    try:
        d = yf.Ticker(sym).history(period="1d", interval="5m")
        if d.empty:
            d = yf.Ticker(sym).history(period="1d")
        return float(d['Close'].iloc[-1]), float(d['High'].max()), float(d['Low'].min())
    except:
        return 0, 0, 0

def atm_strike(spot, step):
    return round(round(spot / step) * step, 2)

def get_signal(spot, ph, pl):
    if spot >= ph and ph > 0:
        return "BUY", "CE"
    if spot <= pl and pl > 0:
        return "SELL", "PE"
    return "WAIT", None

async def start(u, c):
    await u.message.reply_text("🔥 BEST BOT READY!\n\n/nifty - NIFTY LIVE\n/sensex - SENSEX LIVE\n/stockoption - STOCK OPTION\n/commodity - COMMODITY LIVE\n/commodityoption - COMMODITY OPTION")

async def nifty_cmd(u, c):
    spot, ph, pl = live("^NSEI")
    await u.message.reply_text(f"🌞 NIFTY LIVE: {spot:.2f}\nHigh: {ph:.2f} Low: {pl:.2f}\nBuy Above: {ph:.2f} Sell Below: {pl:.2f}")

async def sensex_cmd(u, c):
    spot, ph, pl = live("^BSESN")
    await u.message.reply_text(f"🌞 SENSEX LIVE: {spot:.2f}\nHigh: {ph:.2f} Low: {pl:.2f}")

async def intraday(u, c):
    await u.message.reply_text("Wait...")
    spot, ph, pl = live("^NSEI")
    atm = atm_strike(spot, 50)
    action, opt = get_signal(spot, ph, pl)
    if opt is None:
        await u.message.reply_text(f"📈 INTRADAY NIFTY: {spot:.2f}\nATM: {atm} - WAIT")
    else:
        await u.message.reply_text(f"📈 INTRADAY NIFTY: {spot:.2f}\nATM: {atm} {opt} - {action} Above {ph:.2f}")

async def swing(u, c):
    await u.message.reply_text("📈 SWING - RELIANCE / HDFC / INFY")

async def stockoption(u, c):
    await u.message.reply_text("Wait... STOCK OPTION...")
    out = ""
    for name, sym in [("RELIANCE","RELIANCE.NS"),("HDFC BANK","HDFCBANK.NS"),("INFY","INFY.NS"),("TCS","TCS.NS")]:
        spot, ph, pl = live(sym)
        atm = atm_strike(spot, 20)
        action, opt = get_signal(spot, ph, pl)
        if opt is None:
            out += f"{name} Spot: {spot:.2f} | ATM {atm} - WAIT\n"
        else:
            out += f"{name} Spot: {spot:.2f} | ATM {atm} {opt} - {action} {opt}\n"
    await u.message.reply_text(out)

async def commodity(u, c):
    await u.message.reply_text("Wait... COMMODITY LIVE...")
    out = ""
    for name, cfg in CONFIG.items():
        spot, ph, pl = live(cfg["sym"])
        action, opt = get_signal(spot, ph, pl)
        out += f"{name}: {spot:.2f} - {action}\nBuy Above: {ph:.2f} | Sell Below: {pl:.2f}\n\n"
    await u.message.reply_text(out)

async def commodityoption(u, c):
    await u.message.reply_text("Wait... COMMODITY OPTION...")
    out = ""
    for name, cfg in CONFIG.items():
        spot, ph, pl = live(cfg["sym"])
        action, opt = get_signal(spot, ph, pl)
        if opt is None:
            out += f"{name} Spot: {spot:.2f} - WAIT, No Trade\n\n"
            continue
        atm = atm_strike(spot, cfg["step"])
        entry = round(spot * cfg["prem"], 2 if spot * cfg["prem"] < 5 else 1)
        target, sl = calc(entry)
        out += f"{name} Spot: {spot:.2f} | ATM {atm} {opt} - {action} {opt} 🔥\nEntry: {entry} | Target: {target} | SL: {sl}\n\n"
    await u.message.reply_text(out)

async def get_5_7_signal():
    try:
        t = yf.Ticker("^NSEI")
        d = t.history(period="5d")
        spot = float(d['Close'].iloc[-1])
        ph = float(d['High'].max())
        pl = float(d['Low'].min())
        return spot, ph, pl
    except:
        return None

async def health(req):
    return web.Response(text="OK")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nifty", nifty_cmd))
    app.add_handler(CommandHandler("sensex", sensex_cmd))
    app.add_handler(CommandHandler("intraday", intraday))
    app.add_handler(CommandHandler("swing", swing))
    app.add_handler(CommandHandler("stockoption", stockoption))
    app.add_handler(CommandHandler("commodity", commodity))
    app.add_handler(CommandHandler("commodityoption", commodityoption))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
