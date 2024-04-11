from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint pro příjem otázek a poskytnutí odpovědí
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question', '')

    # Jednoduchá odpověď na otázku
    answer = "Odpověď na otázku: {}".format(question)

    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
