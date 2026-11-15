import os, threading
from flask import Flask
web = Flask(__name__)
@web.route('/')
def home():
    return "Bot is Running!"
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
TOKEN="9245407616:AAHIk3nl7bjFLhehLgSNQEyQ9O7Iz3l_1S0"
S={"Kalyan":"KALYANKJIL.NS","Nazara":"NAZARA.NS"}
def macd(sym):
    try:
        df=yf.download(sym,period="3mo",interval="1d",progress=False)
        c=df['Close']
        m=c.ewm(span=12,adjust=False).mean()
        s=c.ewm(span=26,adjust=False).mean()
        p=float(c.iloc[-1]);q=float(c.iloc[-2])
        ch=(p-q)/q*100
        cr=float(m.iloc[-2])<float(s.iloc[-2]) and float(m.iloc[-1])>float(s.iloc[-1])
        return p,ch,float(m.iloc[-1]),cr
    except:
        return None
async def start(u,c): await u.message.reply_text("Vanakkam! /intraday /swing")
async def intraday(u,c):
    await u.message.reply_text("Wait...")
    t="INTRADAY\n\n"
    for n,sym in S.items():
        r=macd(sym)
        if r:
            p,ch,m,cr=r
            if cr or m>0:
                e="FIRE" if cr else "OK"
                t+=f"{e} {n} Rs.{p:.2f} ({ch:.2f}%)\nEntry {p*1.002:.2f} SL {p*0.985:.2f} TGT {p*1.04:.2f}\n\n"
    await u.message.reply_text(t)
async def swing(u,c):
    await u.message.reply_text("Wait...")
    t="SWING\n\n"
    for n,sym in S.items():
        r=macd(sym)
        if r:
            p,ch,m,cr=r
            if cr:
                t+=f"FIRE {n} Rs.{p:.2f}\nEntry {p*1.002:.2f} SL {p*0.985:.2f} TGT {p*1.04:.2f}\n\n"
    if "FIRE" not in t: t+="No breakout today"
    await u.message.reply_text(t)# ===== NIFTY + SENSEX F&O =====
async def nifty_cmd(u,c):
    await u.message.reply_text("Wait...")
    import yfinance as yf
    d=yf.download("^NSEI",period="5d",interval="1d",progress=False)
    live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
    atm=round(live/50)*50
    if live>ph: t=f"🔥 NIFTY INTRADAY\n{atm} CE BUY\nLive:{live:.0f} > Prev High:{ph:.0f}\nEntry: ATM | Target: +40% | SL: -25%"
    elif live<pl: t=f"🔥 NIFTY INTRADAY\n{atm} PE BUY\nLive:{live:.0f} < Prev Low:{pl:.0f}\nEntry: ATM | Target: +40% | SL: -25%"
    else: t=f"⏳ NIFTY - No Trade\nLive:{live:.0f}\nHigh:{ph:.0f} / Low:{pl:.0f}\nBreakout vandha dhaan Trade!"
    await u.message.reply_text(t)

async def sensex_cmd(u,c):
    await u.message.reply_text("Wait...")
    import yfinance as yf
    d=yf.download("^BSESN",period="5d",interval="1d",progress=False)
    live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
    atm=round(live/100)*100
    if live>ph: t=f"🔥 SENSEX INTRADAY\n{atm} CE BUY\nLive:{live:.0f} > Prev High:{ph:.0f}\nEntry: ATM | Target: +40% | SL: -25%"
    elif live<pl: t=f"🔥 SENSEX INTRADAY\n{atm} PE BUY\nLive:{live:.0f} < Prev Low:{pl:.0f}\nEntry: ATM | Target: +40% | SL: -25%"
    else: t=f"⏳ SENSEX - No Trade\nLive:{live:.0f}\nHigh:{ph:.0f} / Low:{pl:.0f}"
    await u.message.reply_text(t)

async def btst_cmd(u,c):
    await u.message.reply_text("🌙 BTST - NIFTY + SENSEX\nIntraday signal-e BTST ku use pannu veer!\n3 PM ku aprom eduthu, naalaiku 9:30 ku exit!\n/nifty & /sensex adichu paaru!")
app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler('start',start))
app.add_handler(CommandHandler('nifty', nifty_cmd))
app.add_handler(CommandHandler('sensex', sensex_cmd))
app.add_handler(CommandHandler('btst', btst_cmd))
app.add_handler(CommandHandler('intraday',intraday))
app.add_handler(CommandHandler('swing',swing))
def run_web():
    port = int(os.environ.get("PORT", 5000))
    web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()
app.run_polling()
