'''pip install flask-wtf下载flask-wtf扩展'''
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,FileField
from wtforms.validators import DataRequired,InputRequired
from flask_wtf.file import FileAllowed,FileRequired

import os
import random,string
from app import photo


'''导入邮箱格式确认方法和判断值相等的方法,以及raise ValidationError('') 触发验证错误'''
from wtforms.validators import Email,EqualTo,ValidationError
'''注册表单类需引入User模型类'''
from app.models import User

'''pip install Pillow 图片处理库'''
from PIL import Image

class LoginForm(FlaskForm):
    #DataRequired，当你在当前表格没有输入而直接到下一个表格时会提示你输入
    username = StringField('用户名',validators=[DataRequired(message='用户名不为空!')])
    password = PasswordField('密码',validators=[DataRequired(message='密码不为空!')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名',validators=[DataRequired(message='用户名不为空')])
    email = StringField('邮箱',validators=[DataRequired(message='邮箱不为空'),Email()])
    password = PasswordField('密码',validators=[DataRequired(message='密码不为空')])
    password2 = PasswordField('确认密码',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('注册')

    '''解决用户名重复的问题'''
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            '''if为真，触发验证错误，表单会显示错误信息'''
            raise ValidationError('该用户名已注册')
    
    '''解决邮箱重复的问题'''
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已注册')

from wtforms import TextAreaField
from wtforms.validators import Length
class EditProfileForm(FlaskForm):

    username = StringField('昵称',validators=[DataRequired(message='昵称不为空')])
    about_me = TextAreaField('签名',validators=[Length(min=0,max=140)])
    submit = SubmitField('保存')
    


class PostForm(FlaskForm):
    post = TextAreaField('分享你的想法',validators=[DataRequired(),Length(min=1,max=1000)])
    submit = SubmitField('发布')

    
    icon = FileField('',validators=[FileRequired(message='请选择图片'),FileAllowed(photo,message='文件类型不支持上传')])

    '''生成随机的图片名称'''
    def random_name(self,shuffix,length=64):
        Str = string.ascii_letters+string.digits
        return ''.join(random.choice(Str) for i in range(length))+'.'+shuffix

    '''执行图片的缩放'''
    def img_zoom(self,path,prefix,width=200,height=200):
        pass


'''上传图片表单类'''
class UploadForm(FlaskForm):
    icon = FileField('',validators=[FileRequired(message='请选择图片'),FileAllowed(photo,message='错误的文件类型')])
    submit = SubmitField('保存')

    '''生成随机的图片名称'''
    def random_name(self,shuffix,length=64):
        Str = string.ascii_letters+string.digits
        return ''.join(random.choice(Str) for i in range(length))+'.'+shuffix

    '''执行图片的缩放'''
    def img_zoom(self,path,prefix):
        img = Image.open(path)
        img.thumbnail((50,50))
        pathTup = os.path.split(path)
        path = os.path.join(pathTup[0],prefix+pathTup[1])
        img.save(path)
        

    