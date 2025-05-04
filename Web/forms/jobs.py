from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class JobsForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    leader = StringField('Team Leader id', validators=[DataRequired()])
    work_size = IntegerField('Work size')
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finish = BooleanField("Is job finished?")
    submit = SubmitField('add')