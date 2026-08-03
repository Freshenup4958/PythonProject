from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/decor")
def decor():
    return render_template("decor.html")


@app.route("/ideas")
def ideas():
    return render_template("ideas.html")
@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    message = ""

    if request.method == "POST":
        name = request.form["name"]
        message = f"Дякуємо, {name}! ❤️"

    return render_template("feedback.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)