from flask import Flask, render_template, request, jsonify
import asyncio
from main import agent  # Now it safely imports from main.py

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("question")

    async def get_response():
        return await agent.respond(user_input)

    response = asyncio.run(get_response())
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
