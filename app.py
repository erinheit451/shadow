import os
import openai
import json
from flask import Flask, request, Response, redirect, render_template, url_for

with open("prompt.txt") as f:
    prompt = f.read()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/sms", methods=["POST"])
def sms():
    user_input = request.form["Body"]
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{prompt}\n{user_input}",
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6
    )

    # Get the response text
    response_text = response['text']

    # Create a TwiML response
    twiml_response = f"<Response><Message>{response_text}</Message></Response>"

    return Response(twiml_response, mimetype="text/xml")
