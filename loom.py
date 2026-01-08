# flask --app loom run -p 8000
# flask --app loom run -p 8000 --host=0.0.0.0
from .get_data import summary

from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')


@app.route("/")
@app.route("/main_page.html")
def main():
    return render_template('main_page.html', mimetype='text/html', summary=summary)


@app.route("/front.html")
def front():
    return render_template('front.html', mimetype='text/html')


@app.route("/back.html")
def back():
    return render_template('back.html', mimetype='text/html', summary=summary)


@app.route("/final_info.html")
def final_info():
    return render_template('final_info.html', mimetype='text/html', summary=summary)


if __name__ == "__main__":
    app.run(port=8000)
