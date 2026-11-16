import os, threading, asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from aiohttp import web
import yfinance as yf

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
