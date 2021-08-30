'''从app模块中，即从__init__.py中导入创建的myapp应用'''
from app import myapp

'''从flask中导入函数render_template()'''
from flask import render_template

'''导入login_required修饰器，保护页面，强制用户登录'''
from flask_login import login_required


'''current_user:用来获取代表请求客户端的用户对象，也可以是数据库中的用户对象，用户未登录则为特殊的匿名用户对象，
   如果用户名和密码都正确，则调用login_user(),将用户注册为已登录状态，已登录的用户浏览页面时使用current_user代表该用户。
'''
from flask_login import current_user,login_user
from app.models import User


'''从app下的forms模块中导入LoginForm类'''
from app.forms import LoginForm

'''
从flask中导入flash()和redirect()
flash(''.format())闪现
redirect()——对链接路径进行访问、url重定向：redirect("/ccc111")

*url_for()——对函数进行访问、url重定向：redirect(url_for('ccc111'))
render_template()——对html进行渲染的函数：render_template('login.html',title='Sign In',form=form)
'''
from flask import flash,redirect,url_for

'''flask提供的request变量，包含客户端随请求发送的所有信息，并且request.args属性以字典格式公开查询字符串的内容'''
from flask import request

'''导入url_parse()函数，用以解析URL是相对的还是绝对的
   攻击者可能会在next参数中插入指向恶意站点的url。为使应用程序安全，仅在URL是相对的时候才进行重定向，以确保重定向与应用程序位于同一站点内。
   再检查URL的netloc组件是否已设置。
'''
from werkzeug.urls import url_parse

'''导入db,因为注册表单需要通过db.session把新用户的数据上传至数据库'''
from app import db
from app.forms import RegistrationForm


from app.forms import PostForm
from app.models import Post

'''上传路径'''
import os
from app import photo

from app.forms import UploadForm

'''可用在主页也可以不用@login_required'''
'''建立路由器'''
@myapp.route('/')
@myapp.route('/index')

def index():
    
    posts = Post.query.order_by(Post.timestamp.desc()).all()

    '''将需要展示的数据{{title}}和{{user}}传递给index.html进行显示'''
    return render_template('index.html',title='首页',posts=posts)


'''
路由装饰器route()中的参数methods
告诉Flask该视图函数login()接收GET和POST请求，覆盖了默认值GET
HTTP协议指出:GET请求是将信息返回给客户端的请求
POST请求是在浏览器向服务器提交表单时使用的
'''
@myapp.route('/login',methods=['GET','POST'])
def login():
    '''如果current_user具有有效凭据，即用户已登录，重定向至首页'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    '''创建登录表单LoginForm类的实例'''
    form=LoginForm()
    
    '''form.validate_on_submit()方法完成所有表单处理工作
       当用户按下提交按钮而发送POAT请求时，此函数将收集表单中的数据
    '''
    if form.validate_on_submit():

        #flash('Login requested for user {},remember_me={}'.format(form.username.data,form.remember_me.data))
        '''将用户重定向至应用程序的index.html页面'''
        #return redirect(url_for('index'))

        '''根据表单中的用户名查询User表'''    
        user = User.query.filter_by(username=form.username.data).first()
        '''如果查询为空或者表单中的密码验证user表失败，说明用户名为空或者密码错误，重定向至登录页'''
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误！')
            return redirect(url_for('login'))
        '''登录成功的话，就将用户注册为已登录状态，用户浏览页面时使用current_user代表自己'''
        login_user(user,remember=form.remember_me.data)

        '''login_user()登录成功后，立即使用request.args.get('next')方法获得查询字符串参数‘next’的值，并赋给next_page'''
        next_page = request.args.get('next')

        '''登录URL没有next参数，或者登录URL的next参数设置为包含域名的完整URL的参数，重定向至index索引页,保护应用程序以防恶意站点的url插入'''
        if not next_page or url_parse(next_page).netloc !='':
            next_page = url_for('index')

        '''否则，登录URL的next参数是相对路径的参数，即没有域部分的URL，安全，可以直接重定向到该URL，用以实现用户登录成功后的页面跳转问题'''
        return redirect(next_page)        
            
    '''将login.html需要展示的数据{{title}}和{{form}}传递给templates进行渲染'''
    return render_template('login.html',title='登录',form=form)


'''导入flask_login的logout_user()函数实现注销功能'''
from flask_login import logout_user
@myapp.route('/logout')
def logout():
    '''取消用户的登录状态，与login_user()功能相反'''
    logout_user()
    return redirect(url_for('index'))

'''注册表单需要设置methods参数，POST请求是在浏览器向服务器提交表单时使用的'''
@myapp.route('/register',methods=['GET','POST'])
def register():
    '''如果用户已登录，直接重定向至首页'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    '''创建注册表单类的实例'''
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username = form.username.data,email=form.email.data)
        '''将表单中的密码变成哈希密码存入数据库'''
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！')
        return redirect(url_for('login'))
    return render_template('/register.html',title='登录',form=form)



'''函数映射到URL:/user/<username>
   该<username>组件表示为<被包围的URL组件>
   当路由具有动态成分时，Flask将接受URL<>部分中的任何文本，并作为参数来调用视图函数user(username)
'''
@myapp.route('/user/<username>')
@login_required
def user(username):

    '''first_or_404()：first()的变体，在没有结果的情况下会返回404错误到客户端'''
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    '''如果当前用户访问其他用户时'''
    if username != current_user.username:
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    return render_template('user.html',title='我的',user=user,posts=posts)

from datetime import datetime

''''''
@myapp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

from app.forms import EditProfileForm
@myapp.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    form1 = UploadForm()
    user = User.query.filter_by(username=current_user.username).first_or_404()
    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('您的更改已保存')
        return redirect(url_for('user',username=current_user.username))
          
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',user=user,title='编辑个人信息',form=form,form1=form1)


@myapp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    
    if user == current_user:
        flash('不能关注自己')
        return redirect(url_for('user',username=username))
    
    '''user.follow(user)已写好的关注方法'''
    current_user.follow(user)
    db.session.commit()
    flash('关注用户：{}成功'.format(username))
    return redirect(url_for('user',username=username))

@myapp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    
    if user == current_user:
        flash('不能关注自己')
        return redirect(url_for('user',username=username))
    
    current_user.unfollow(user)
    db.session.commit()
    flash('取消关注用户：{}成功'.format(username))
    return redirect(url_for('user',username=username))



@myapp.route('/post',methods=['GET','POST'])
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
        photo.save(icon,name=imgName)

        '''通过图片名称，拿到url地址'''
        img_url = photo.url(imgName)

        post = Post(body = form.post.data,author=current_user,post_photo_url=img_url)
        db.session.add(post)
        db.session.commit()
        flash('动态发布成功')
        redirect(url_for('post'))

    posts= current_user.followed_posts().all()

    return render_template("post.html",title='动态',form=form,posts=posts)



@myapp.route('/uploads/',methods=['GET','POST'])
@login_required
def uploads():
    form = UploadForm()
    img_url = None

    if form.validate_on_submit():
        icon = request.files.get('icon')
        suffix = icon.filename.split('.')[-1] #获取后缀

        while True:
            imgName = form.random_name(suffix)
            path = os.path.join(myapp.config['UPLOADS_DEFAULT_DEST'],imgName)

            if not os.path.exists(path):
                break

        photo.save(icon,name=imgName)
        img_url = photo.url(imgName)
        current_user.user_photo = img_url
        db.session.commit()
        flash('您的更改已保存')
        return redirect(url_for('edit_profile',user=current_user))
    return render_template('uploads.html',form=form,user=current_user)
