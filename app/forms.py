from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired

class SearchForm(FlaskForm):
	location = StringField('Location',validators=[DataRequired()])
	area = StringField('Area',validators=[DataRequired()])
	type_room = SelectField('Type of room', choices=[('Private room', 'Private room'), ('Entire home/apt', 'Entire home/apt'), ( 'Shared room', 'Shared room')])
	start_date = StringField('Start date')
	end_date = StringField('End date')
	guest = StringField('Number of guests')
	price_1 = StringField('Price from')
	price_2 = StringField('Price to')
	submit = SubmitField('Search')


