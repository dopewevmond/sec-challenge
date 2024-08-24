from flask import Flask, render_template
from forms import CVEForm
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/", methods=["GET", "POST"])
def search_cve():
    form = CVEForm()
    if form.validate_on_submit():
        cve = form.cve.data
    return render_template("index.html", form=form)
