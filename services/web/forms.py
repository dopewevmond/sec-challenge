from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CVEForm(FlaskForm):
    cve = StringField(
        "Enter the CVE ID below",
        validators=[DataRequired("Please enter a CVE ID and try again")],
    )
    submit = SubmitField("Search for CVE")
