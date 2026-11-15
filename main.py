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
    try:
        import yfinance as yf
        out="🔥 INTRADAY - NIFTY + SENSEX\n\n"
        for name,sym,step in [("NIFTY","^NSEI",50),("SENSEX","^BSESN",100)]:
            d=yf.Ticker(sym).history(period="5d")
            live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
            atm=round(live/step)*step
            if live>ph: out+=f"{name}: {atm} CE BUY | Live:{live:.0f} > {ph:.0f}\n\n"
            elif live<pl: out+=f"{name}: {atm} PE BUY | Live:{live:.0f} < {pl:.0f}\n\n"
            else: out+=f"{name}: No Trade | Live:{live:.0f}\nHigh:{ph:.0f} / Low:{pl:.0f}\n\n"
        t=out
    except Exception as e:
        t=f"INTRADAY error: {e}"
    await u.message.reply_text(t)
async def swing(u,c):
    await u.message.reply_text("Wait...")
    try:
        import yfinance as yf
        out="📈 SWING - NIFTY + SENSEX\n\n"
        for name,sym,step in [("NIFTY","^NSEI",50),("SENSEX","^BSESN",100)]:
            d=yf.Ticker(sym).history(period="10d")
            live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
            atm=round(live/step)*step
            if live>ph: out+=f"{name}: {atm} CE BUY | BREAKOUT!\nLive:{live:.0f} > {ph:.0f}\nTarget:+200 | SL:{ph:.0f}\n\n"
            elif live<pl: out+=f"{name}: {atm} PE BUY | BREAKDOWN!\nLive:{live:.0f} < {pl:.0f}\nTarget:-200 | SL:{pl:.0f}\n\n"
            else: out+=f"{name}: No Breakout | Live:{live:.0f}\nHigh:{ph:.0f} / Low:{pl:.0f}\n\n"
        t=out
    except Exception as e:
        t=f"SWING error: {e}"
    await u.message.reply_text(t)
async def nifty_cmd(u,c):
    await u.message.reply_text("Wait...")
    try:
        import yfinance as yf
        d=yf.Ticker("^NSEI").history(period="5d")
        live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
        atm=round(live/50)*50
        if live>ph: t=f"🔥 NIFTY INTRADAY\n{atm} CE BUY\nLive:{live:.0f} > Prev High:{ph:.0f}"
        elif live<pl: t=f"🔥 NIFTY INTRADAY\n{atm} PE BUY\nLive:{live:.0f} < Prev Low:{pl:.0f}"
        else: t=f"⏳ NIFTY - No Trade\nLive:{live:.0f}\nHigh:{ph:.0f} / Low:{pl:.0f}"
    except Exception as e:
        t=f"NIFTY error: {e}"
    await u.message.reply_text(t)

async def sensex_cmd(u,c):
    await u.message.reply_text("Wait...")
    try:
        import yfinance as yf
        d=yf.Ticker("^BSESN").history(period="5d")
        live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
        atm=round(live/100)*100
        if live>ph: t=f"🔥 SENSEX INTRADAY\n{atm} CE BUY\nLive:{live:.0f} > Prev High:{ph:.0f}"
        elif live<pl: t=f"🔥 SENSEX INTRADAY\n{atm} PE BUY\nLive:{live:.0f} < Prev Low:{pl:.0f}"
        else: t=f"⏳ SENSEX - No Trade\nLive:{live:.0f}\nHigh:{ph:.0f} / Low:{pl:.0f}"
    except Exception as e:
        t=f"SENSEX error: {e}"
    await u.message.reply_text(t)

async def btst_cmd(u,c):
 await u.message.reply_text("🌙 BTST - NIFTY + SENSEX\nIntraday signal-e BTST ku use pannu veer!\n3 PM ku aprom eduthu, naalaiku 9:30 ku exit!\n/nifty & /sensex adichu paaru!")
async def commodity(u,c):
    await u.message.reply_text("Wait...")
    try:
        import yfinance as yf
        out="🪙 COMMODITY\n\n"
        for name,sym in [("GOLD","GC=F"),("SILVER","SI=F"),("CRUDE","CL=F"),("NAT GAS","NG=F")]:
            d=yf.Ticker(sym).history(period="5d")
            live=float(d['Close'].iloc[-1]); ph=float(d['High'].iloc[-2]); pl=float(d['Low'].iloc[-2])
            if live>ph: out+=f"{name}: BUY ABOVE {ph:.1f} | Live:{live:.1f}\n\n"
            elif live<pl: out+=f"{name}: SELL BELOW {pl:.1f} | Live:{live:.1f}\n\n"
            else: out+=f"{name}: No Trade | Live:{live:.1f}\nHigh:{ph:.1f} / Low:{pl:.1f}\n\n"
        t=out
    except Exception as e:
        t=f"COMMODITY error: {e}"
    await u.message.reply_text(t)
    

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
