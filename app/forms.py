from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,SelectField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from flask_wtf.file import FileField,FileAllowed
class RegisterForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired(),Length(min=2,max=80)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired(),Length(min=6)])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Register')
class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')
class JobForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired(),Length(min=2,max=150)])
    short_desc=StringField('Short Description',validators=[DataRequired(),Length(min=2,max=300)])
    full_desc=TextAreaField('Full Description',validators=[DataRequired()])
    company=StringField('Company',validators=[DataRequired(),Length(min=2,max=120)])
    salary=StringField('Salary')
    location=StringField('Location')
    category=SelectField('Category',choices=[('IT','IT'),('Design','Design'),('Marketing','Marketing'),('Finance','Finance'),('HR','HR')])
    submit=SubmitField('Add Job')
class ProfileForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired(),Length(min=2,max=80)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    image=FileField('Profile Image',validators=[FileAllowed(['jpg','jpeg','png'],'Images only!')])
    submit=SubmitField('Update Profile')
class AdminUserForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired(),Length(min=2,max=80)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired(),Length(min=6)])
    role=SelectField('Role',choices=[('user','User'),('admin','Admin')],validators=[DataRequired()])
    submit=SubmitField('Add User')
