import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from aiohttp import web
import yfinance as yf

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
    except Exception as e:
        print(f"Live error {sym}: {e}")
        return 0, 0, 0

def atm_strike(spot, step):
    return round(round(spot / step) * step, 2)
    import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from aiohttp import web
import yfinance as yf

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
    except Exception as e:
        print(f"Live error {sym}: {e}")
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
        await u.message.reply_text(f"📈 INTRADAY NIFTY: {spot:.2f}\nATM: {atm} {opt} - {action}")

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

async def health(request):
    return web.Response(text="OK")

async def main():
    if not TOKEN:
        print("ERROR: BOT_TOKEN not found!")
        return
    print("Bot starting...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nifty", nifty_cmd))
    app.add_handler(CommandHandler("sensex", sensex_cmd))
    app.add_handler(CommandHandler("intraday", intraday))
    app.add_handler(CommandHandler("swing", swing))
    app.add_handler(CommandHandler("stockoption", stockoption))
    app.add_handler(CommandHandler("commodity", commodity))
    app.add_handler(CommandHandler("commodityoption", commodityoption))
    webapp = web.Application()
    webapp.router.add_get("/", health)
    runner = web.AppRunner(webapp)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on {port}")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("Bot polling started - LIVE")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
