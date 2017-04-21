from flask_wtf import FlaskForm
from wtforms.validators import Required
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, HiddenField
from wtforms import FileField
from wtforms import SelectField

class RegistrationForm(FlaskForm):
	email = StringField('Email', validators=[Required()])
	username = StringField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Register')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Login')

class PostForm(FlaskForm):
	title = StringField('Title', validators=[Required()])
	tags = StringField('Tags', validators=[Required()])
	category = SelectField('Category', choices=[('movies', 'Movies'),
												('articles', 'Articles'),
												('songs', 'Songs'),
												('books', 'Books')])
	link = StringField('Link', validators=[Required()])
	text = TextAreaField('Text', validators=[Required()])
	image = FileField('Image')
	submit = SubmitField('Post')

class FollowForm(FlaskForm):
	email = HiddenField('Email', validators=[Required()])
	make_friends = SubmitField('Follow')

class UnfollowForm(FlaskForm):
	email = HiddenField('Email', validators=[Required()])
	unfollow = SubmitField('Unfollow')

class LikePostForm(FlaskForm):
	post_id = HiddenField('id', validators=[Required()])
	submit = SubmitField('Like')