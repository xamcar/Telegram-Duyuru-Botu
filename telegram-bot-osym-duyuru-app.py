import logging
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup

# Telegram botunun kimlik bilgilerini ve API URL'sini tanımla
BOT_TOKEN = "6286188900:AAGIC7JcPE-EMZ-bzmi-Yc8Z1GHAwGW1eB4"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Günlük kaydını etkinleştir
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Command handler for /start command"""
    update.message.reply_text('Bot çalışır durumda!')

def help(update: Update, context: CallbackContext) -> None:
    """Command handler for /yardim command"""
    update.message.reply_text('"/start" Bot Durumu! \n"/duyuru" Güncel Duyurular! \n"/yardim" Komut Listesi!')

def echo(update: Update, context: CallbackContext) -> None:
    """Handler for text messages other than commands"""
    update.message.reply_text("Geçersiz Komut!")

def error(update: Update, context: CallbackContext) -> None:
    """Error handler"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def telegram_bot_sendtext(bot_message: str, chat_id: str) -> None:
    """Send text message via Telegram bot"""
    send_text = BASE_URL + f"sendMessage?chat_id={chat_id}&text={bot_message}&parse_mode=HTML"
    response = requests.get(send_text)
    if response.status_code == 200:
        logger.info("Message sent successfully")
    else:
        logger.error("Failed to send message")

def getAnnouncement(update: Update, context: CallbackContext) -> None:
    """Command handler for /duyuru command"""
    # Web sitesinden sayfa içeriğini al
    url = "https://www.osym.gov.tr/"
    response = requests.get(url, verify=False)
    content = response.content

    # BeautifulSoup kullanarak sayfayı çözümle
    soup = BeautifulSoup(content, "html.parser")

    # col-sm-5 news timeline absoluteBoxElement2 sınıfına sahip öğeleri bul
    elements = soup.find_all(class_="col-sm-5 news timeline absoluteBoxElement2")

    # Öğelerin içindeki li etiketlerini bul ve a etiketlerinin metnini ve bağlantısını getir
    announcements = []
    for element in elements:
        li_tags = element.find_all("li")
        for li_tag in li_tags:
            a_tag = li_tag.find("a")
            if a_tag:
                text = a_tag.text.strip()
                link = url + a_tag['href']
                announcement = f'<a href="{link}">{text}</a>'
                announcements.append(announcement)
    
    if announcements:
        message = "Güncel Duyurular:\n\n" + "\n\n".join(announcements)
        telegram_bot_sendtext(message, update.effective_chat.id)
    else:
        update.message.reply_text("Güncel duyuru bulunamadı.")

def main() -> None:
    """Start the bot"""
    # Telegram botunun güncellemelerini almak için bir Updater oluştur
    updater = Updater(BOT_TOKEN)

    # Komut işleyicilerini kaydet
    dispatcher = updater.dispatcher

    # Komut işleyicilerini ekle
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("yardim", help))
    dispatcher.add_handler(CommandHandler("duyuru", getAnnouncement))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Hata işleyicisini ekle
    dispatcher.add_error_handler(error)

    # Botu başlat
    updater.start_polling()

    # Ctrl-C'ye veya SIGINT/SIGTERM/SIGABRT sinyallerine basılana kadar botu çalıştır
    updater.idle()

if __name__ == '__main__':
    main()
