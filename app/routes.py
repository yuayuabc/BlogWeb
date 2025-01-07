from app import myapp
from flask import render_template
from flask_login import login_required
from flask_login import current_user, login_user
from app.models import User
from app.forms import LoginForm
from flask import flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.forms import PostForm
from app.models import Post
import os
from app import photo
from app.forms import UploadForm
from datetime import datetime
from app.forms import EditProfileForm

@myapp.route('/')
@myapp.route('/index')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',title = '首页', posts = posts)

@myapp.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():  
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误！')
            return redirect(url_for('login'))
        login_user(user,remember = form.remember_me.data)
        next_page = request.args.get('next')
        '''登录URL没有next参数，或者登录URL的next参数设置为包含域名的完整URL的参数，重定向至index索引页,保护应用程序以防恶意站点的url插入'''
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        '''否则，登录URL的next参数是相对路径的参数，即没有域部分的URL，安全，可以直接重定向到该URL，用以实现用户登录成功后的页面跳转问题'''
        return redirect(next_page)        
    return render_template('login.html',title = '登录', form = form)

from flask_login import logout_user
@myapp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@myapp.route('/register',methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        '''将表单中的密码变成哈希密码存入数据库'''
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！')
        return redirect(url_for('login'))
    return render_template('/register.html', title = '登录', form = form)

@myapp.route('/user/<username>')
@login_required
def user(username):

    '''first_or_404()：first()的变体，在没有结果的情况下会返回404错误到客户端'''
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(user_id = current_user.id).order_by(Post.timestamp.desc()).all()
    '''如果当前用户访问其他用户时'''
    if username != current_user.username:
        posts = Post.query.filter_by(user_id = user.id).order_by(Post.timestamp.desc()).all()
    return render_template('user.html', title = '我的', user = user, posts = posts)

@myapp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@myapp.route('/edit_profile',methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    form1 = UploadForm()
    user = User.query.filter_by(username = current_user.username).first_or_404()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('您的更改已保存')
        return redirect(url_for('user',username = current_user.username))
          
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', user = user, title = '编辑个人信息', form = form, form1 = form1)


@myapp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('不能关注自己')
        return redirect(url_for('user', username = username))    
    current_user.follow(user)
    db.session.commit()
    flash('关注用户：{}成功'.format(username))
    return redirect(url_for('user', username = username))

@myapp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('不能关注自己')
        return redirect(url_for('user', username = username))
    current_user.unfollow(user)
    db.session.commit()
    flash('取消关注用户：{}成功'.format(username))
    return redirect(url_for('user', username = username))

@myapp.route('/post',methods = ['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    img_url = None
    if form.validate_on_submit():
        icon = request.files.get('icon')
        suffix = icon.filename.split('.')[-1] #获取后缀
        '''循环获取唯一的图片名称'''
        while True:
            imgName = form.random_name(suffix)
            path = os.path.join(myapp.config['UPLOADS_DEFAULT_DEST'],imgName)
            if not os.path.exists(path):
                break
        '''保存文件，文件名随机'''
        photo.save(icon,name = imgName)

        '''通过图片名称，拿到url地址'''
        img_url = photo.url(imgName)

        post = Post(body = form.post.data, author = current_user, post_photo_url = img_url)
        db.session.add(post)
        db.session.commit()
        flash('动态发布成功')
        redirect(url_for('post'))
    posts = current_user.followed_posts().all()
    return render_template("post.html", title ='动态', form = form,posts = posts)

@myapp.route('/uploads/', methods = ['GET', 'POST'])
@login_required
def uploads():
    form = UploadForm()
    img_url = None
    if form.validate_on_submit():
        icon = request.files.get('icon')
        suffix = icon.filename.split('.')[-1] #获取后缀
        while True:
            imgName = form.random_name(suffix)
            path = os.path.join(myapp.config['UPLOADS_DEFAULT_DEST'], imgName)
            if not os.path.exists(path):
                break
        photo.save(icon, name = imgName)
        img_url = photo.url(imgName)
        current_user.user_photo = img_url
        db.session.commit()
        flash('您的更改已保存')
        return redirect(url_for('edit_profile', user = current_user))
    return render_template('uploads.html',form = form, user = current_user)
