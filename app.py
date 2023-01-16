import os
import openai
import telegram
import logging
from flask import Flask, request, Response, redirect, render_template, url_for
from telegram.ext import Updater, CommandHandler, MessageHandler, message, Filters
from prompt import prompt

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
bot_token = os.environ["BOT_TOKEN"]
bot = telegram.Bot(token=bot_token)
conversation = []

@app.route("/", methods=("GET", "POST"))
def index():

    #kill
    return
    
    global conversation
    # Handle form submission
    if request.method == "POST":
        user_input = request.form["input"]
        conversation.append({"user": user_input})
        # Generate a response from the chatbot
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{prompt}{user_input}",
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
    )

        chatbot_response = response.choices[0].text
        conversation.append({"chatbot": chatbot_response})
    return render_template("index.html", conversation=conversation)

@app.route("/sms", methods=["POST"])
def sms():
    # Get the message body from the request
    body = request.form["Body"]
    # Generate a response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{prompt}{body}",
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    chatbot_response = response.choices[0].text
    # Create a TwiML response
    twiml_response = f"<Response><Message>{chatbot_response}</Message></Response>"
    return Response(twiml_response, mimetype="text/xml")



updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

# Define the /start command handler
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am a bot that is integrated with the OpenAI GPT-3 API. You can ask me any question and I will try to provide a response.")

# Define the /help command handler
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="To use me, simply send me a message with your question. I will use the OpenAI GPT-3 API to generate a response based on the information I get.") 

@app.route("/webhook", methods=["POST"])
def webhook():
    # Get the update from Telegram
    update = request.get_json()
    
    # Check if the update contains a 'message'
    if 'message' in update:
        message_text = update['message']['text']
        chat_id = update['message']['chat']['id']
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=message_text,
            max_tokens=250,
            temperature=0.7
    )
    bot.send_message(chat_id=chat_id, text=response["choices"][0]["text"])
    # Return a 200 OK response
    return "OK"

updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(MessageHandler(Filters.text, message))
# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

updater.start_polling()


if __name__ == '__main__':
    app.run()
