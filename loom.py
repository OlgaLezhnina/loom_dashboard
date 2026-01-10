# flask --app loom run -p 8000
# flask --app loom run -p 8000 --host=0.0.0.0
from .get_data import summary

from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')


@app.route("/")
@app.route("/main_page.html")
def main():
    return render_template('main_page.html', mimetype='text/html', summary=summary)


@app.route("/cards_front.html")
def cards_front():
    return render_template('cards_front.html', mimetype='text/html', summary=summary)


@app.route("/cards_back.html")
def cards_back():
    return render_template('cards_back.html', mimetype='text/html')


@app.route("/detailed_information.html")
def detailed_information():
    return render_template('detailed_information.html', mimetype='text/html', summary=summary)


if __name__ == "__main__":
    app.run(port=8000)
