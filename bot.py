import telebot
import yt_dlp
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir localmente)
load_dotenv()

# Busca o token da variável de ambiente. Se não achar, para o script.
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Token do bot não encontrado! Verifique o arquivo .env ou as variáveis do sistema.")

bot = telebot.TeleBot(TOKEN)

# --- Handler de YouTube ---
@bot.message_handler(func=lambda m: 'youtube.com' in m.text or 'youtu.be' in m.text)
def download_youtube_audio(message):
    url = message.text
    chat_id = message.chat.id
    
    msg_temp = bot.reply_to(message, "⏳ Baixando e convertendo áudio...")
    print(f"Iniciando download para: {chat_id}")

    # Opções do yt-dlp para MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s', # Nome temporário
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True
    }

    filename = ""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Recupera o nome exato do arquivo gerado
            filename = f"{ydl.prepare_filename(info).rsplit('.', 1)[0]}.mp3"

        # Envia o arquivo
        with open(filename, 'rb') as audio:
            bot.send_audio(chat_id, audio, title=info.get('title', 'Audio'), performer=info.get('uploader', 'YouTube'))
        
        bot.delete_message(chat_id, msg_temp.message_id)
        print("Envio concluído.")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erro: {str(e)}")
        print(f"Erro: {e}")
        
    finally:
        # Limpeza do container
        if filename and os.path.exists(filename):
            os.remove(filename)

# --- Start ---
print("Bot NeoTools rodando...")
bot.polling()