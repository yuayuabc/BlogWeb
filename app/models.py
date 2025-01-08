from app import db

'''从werkzeug.security模块中导入哈希密码的生成函数generate_password_hash()和检验函数check_password_hash'''
from werkzeug.security import generate_password_hash,check_password_hash

'''导入被称为mixin的类UserMixin,类中包含大多数用户模型类的通用实现方法的接口'''
from flask_login import UserMixin

from hashlib import md5

from datetime import datetime

'''追随者关联表，由user的主码id构成'''
followers = db.Table('followers',
    db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer,db.ForeignKey('user.id'))
)


'''创建User数据模型用户表的类User,继承自Flask-SQLAlchemy中所有模型的基类db.Model'''
'''将UserMixin类添加至用户模型中'''
class User(UserMixin,db.Model):
    '''创建表的属性'''
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120),index=True,unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.now)
    user_photo = db.Column(db.String(140))

    '''
    创建用户User与帖子Post之间关系的高级视图,而不是实际的表属性
    backref参数将添加指向一个对象的许多类的对象的字段，即添加post.author返回给用户的帖子
    lazy参数定义发出有关该关系的数据库查询的方法dynamic
    '''
    posts = db.relationship('Post',backref='author',lazy='dynamic')

    followed = db.relationship(
        'User',#自我参照关系，参照User表，即关系的右侧的表为User
        secondary=followers,#配置关系followed的关联表为followers表
        primaryjoin=(followers.c.follower_id == id),#左侧实体(关注者用户)与关联表链接的条件
        secondaryjoin=(followers.c.followed_id == id),#右侧实体(被关注用户)与关联表链接的条件
        backref=db.backref('followers',lazy='dynamic'),#右侧实体(被关注用户)访问关系followed的方法'user.followers.xxx'
        lazy='dynamic')#左侧实体(关注者用户)访问关系followed的方法


    def __repr__(self):
        return '<User {}>'.format(self.username)

    '''将password通过哈希密码生成函数，生成哈希密码赋给表中的password_hash字段'''
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    '''将password与表中的password_hash字段进行比较，返回布尔值'''
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    '''获取用户头像URL的方法'''
    def avatar(self,size):
        '''返回一串随机字符串'''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)

    def defaultBaseAvatar(self):
        imgStr = 'data:image/svg+xml;charset=utf-8;base64,PHN2ZyB0PSIxNzM1NTU1MTk0MTE5IiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjI2ODYiIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIj48cGF0aCBkPSJNOTA4LjU0OCAyMDUuNjYxIDU4Mi40NTQgMjAuNDc5QzU2MC40OTUgNy45NzkgNTM2LjAzNyAxLjc4NSA1MTEuNTc4IDEuNzg1Yy0yNC40NTggMC00OC45MTcgNi4xOTQtNzAuODc1IDE4LjY5M0wxMTQuNTkxIDIwNS42NjFjLTQ0LjQ5NiAyNS4yOTgtNzEuOTc2IDcyLjMxMi03MS45NzYgMTIzLjI4MWwwIDM2Ny45MDJjMCA1MC45MzIgMjcuNDggOTcuOTgyIDcxLjk3NiAxMjMuMjQybDMyNi4xMTIgMTg1LjIyM0M0NjIuNjYxIDEwMTcuNzcgNDg3LjEyIDEwMjQgNTExLjU3OCAxMDI0YzI0LjQ1OSAwIDQ4LjkxNy02LjIzIDcwLjg3Ni0xOC42OTFsMzI2LjA5NC0xODUuMjIzYzQ0LjUxNC0yNS4yNiA3MS45NzUtNzIuMzExIDcxLjk3NS0xMjMuMjQyTDk4MC41MjMgMzI4Ljk0MkM5ODAuNTIyIDI3Ny45NzMgOTUzLjA2MiAyMzAuOTU5IDkwOC41NDggMjA1LjY2MXpNNTQ4LjI1NyA5NDUuODNjLTExLjE1NSA2LjMwNy0yMy44NDMgOS42NjQtMzYuNjc5IDkuNjY0LTEyLjg1NCAwLTI1LjU0MS0zLjM1Ny0zNi42NzktOS42NjRMMjM1LjQyNyA4MDkuODI2YzE1LjU5Ny04LjU4IDMxLjYyMy0xNC41NTEgNDUuMjYtMTUuNzA5IDE2LjUzLTEuNDE4IDM5LjY0NS03LjE2MiA2NC4xMjMtMTMuMjQ2IDkuMTc5LTIuMzEzIDE4LjQxNC00LjU4OCAyNy4xNDUtNi42MDQgNTEuNTQ3LTExLjkwMiA2OC43NDktMjIuNzIzIDc3LjE5OS0yOS44NSA3LjkzLTYuNjggMTIuMzg4LTE2LjUyOSAxMi4yMDItMjYuODY1LTAuNTA0LTIyLjUtOC4yMDktNDQuNDAyLTIyLjQyNS02My42MTktMi4yNTgtMy45NTUtNS4zMTctNy40MjQtOC45OTMtMTAuMjIzLTQ2LjgyNy0zNS42MzUtNzQuNzkzLTk3LjIzNi03NC43OTMtMTY0LjczNCAwLTEwNi42NCA3MC41MDMtMTkzLjM5MyAxNTcuMTYyLTE5My4zOTMgODYuNjQgMCAxNTcuMTIzIDg2LjY0IDE1Ny4xMjMgMTkzLjIwNCAwIDY3LjM1LTI3Ljk2NiAxMjguODAzLTc0Ljc5MyAxNjQuNDM4LTIuMjM4IDEuNjgtNC4zMjggMy43NjgtNi4xMDEgNS45NjktMTYuMzA2IDIwLjQxLTI0Ljc5NCA0Mi43Ni0yNS4yOTcgNjYuMzc5LTAuMTg4IDEwLjI2MiA0LjIxNiAyMC4wMzkgMTIuMDE0IDI2LjcxNyA3LjU5NCA2LjQ1NSAyMy4xNzMgMTUuNDg0IDc2LjY2IDI3LjkwOCAzMi4yMzcgNy41MzkgNjkuNDc1IDE0LjAzMSA5MC41MiAxNS44MjIgMTcuODE2IDEuNTY2IDM3Ljc2IDguMzU3IDU1LjUwMyAxNy45ODJMNTQ4LjI1NyA5NDUuODN6TTkxMS42MDcgNjk2Ljg0NGMwIDI2LjI2OC0xNC4yNzMgNTAuNzQ0LTM3LjI1NyA2My44MDVsLTkuOTgxIDUuNjcyYy0wLjMzNy0wLjI5OS0wLjQ2Ni0wLjcwOS0wLjgwMy0wLjk3MS0zMi4zMTItMjYuMzQyLTc1LjM3LTQ0LjEwNC0xMTUuMTg0LTQ3LjUzNy0xNy41NzQtMS41MjktNTIuMjc1LTcuNjg2LTgwLjc0NS0xNC4zMjYtMTEuOTc4LTIuNzYyLTIxLjI0OS01LjIyNS0yOC4yODItNy4yNCAwLjM1NS0wLjU1OSAwLjcyOC0xLjExNyAxLjEzOC0xLjcxNSA2MS4zNjEtNDguODQ0IDk3Ljg3LTEyOS4wMjcgOTcuODctMjE1Ljc0MyAwLTE0NC4zMjQtMTAxLjQxNS0yNjEuNzA5LTIyNi4wNTctMjYxLjcwOS0xMjQuNjggMC0yMjYuMDc3IDExNy40Ni0yMjYuMDc3IDI2MS44OTggMCA4Ni40OSAzNi4xOTMgMTY2LjUyNSA5Ny4wODcgMjE1LjQwNiAxLjIxMiAxLjY0MSAyLjI5NCAzLjI4MyAzLjI4MyA1LTcuMjM5IDIuMzEzLTE3LjA3MSA1LjExMS0zMC4yNDIgOC4xMzMtOS4xMjMgMi4xMjctMTguNzMgNC41MTYtMjguMjY0IDYuOTAyLTE5LjgzMiA0LjkyNi00Mi4yOTMgMTAuNDg0LTUzLjMyIDExLjQ1NS0zNC40NzcgMi45NDctNzMuMjgxIDIwLjI5Ny0xMDUuOCA0Ni4xOTNsLTIwLjE4Ni0xMS40MThjLTIyLjk2NS0xMy4wNjEtMzcuMjU2LTM3LjUzNy0zNy4yNTYtNjMuODA1TDExMS41MzEgMzI4Ljk0MmMwLTI2LjMwNiAxNC4yOTEtNTAuNzQ1IDM3LjI1Ni02My44MDRsMzI2LjExMi0xODUuMjJjMTEuMTM4LTYuMzA2IDIzLjgyNC05LjY2NCAzNi42NzktOS42NjQgMTIuODM2IDAgMjUuNTIzIDMuMzU3IDM2LjY3OSA5LjY2NGwzMjYuMDk0IDE4NS4yMmMyMi45ODMgMTMuMDYgMzcuMjU3IDM3LjQ5OSAzNy4yNTcgNjMuODA0TDkxMS42MDggNjk2Ljg0NHoiIGZpbGw9IiM1MTUxNTEiIHAtaWQ9IjI2ODciPjwvcGF0aD48L3N2Zz4='
        return imgStr

    def follow(self,user):
        '''如果当前用户不在被关注用户项中'''
        if not self.is_following(user):
            '''关系followed的属性append(user),表示添加'''
            self.followed.append(user)

        '''即，如果当前用户未被关注，就可以选择关注'''


    def unfollow(self,user):
        '''如果当前用户已被关注，可以选择移除用户，即取消关注'''
        if self.is_following(user):
            self.followed.remove(user)

    '''返回在关联表中followed_id被关注者项是user.id的数目  > 0 ，即返回当前user_id 是否被关注的布尔值'''
    def is_following(self,user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0



    '''返回被当前用户关注的用户的帖子，以及自己的帖子，并按帖子的时间排序'''
    def followed_posts(self):
        
        '''
        return Post.query.join(followers,(followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(
                Post.timestamp.desc())
        Post.query.join().filter().order_by()
        
        filter出followed表中的元组，条件是关注者id与当前用户id相同
        Post表的id , followed表中被filter的元组的被关注项的id ， 相同的话就关联，
        最后按post的时间排序
        '''


        '''查询出当前用户关注的用户，所发出的帖子'''
        followed=Post.query.join(followers,(followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        
        '''查询出用户自己所发出的帖子'''
        own = Post.query.filter_by(user_id=self.id)
        
        '''合并两类帖子，并排序，返回'''
        return followed.union(own).order_by(Post.timestamp.desc())
    
        



'''
从app包中导入Flask-Login的实例login
包含四个必要的方法：
is_authenticated：一个属性，如果用户具有有效的凭据，则为 True
is_active：一个属性，如果用户帐户处于活动状态，则为 True
is_anonymous：一个属性，对于普通用户为 False,对于特殊的匿名用户来说为 True
get_id()：一种以字符串形式返回用户唯一标识符的方法
'''
from app import login
'''用户加载程序在 Flask-Login 中注册"@login.user_loader" 修饰器'''
@login.user_loader
def load_user(id):
    '''用户加载器功能：
       Flask-Login通过将用户唯一标识符存储在用户会话中的方法，跟踪已登录的用户
       每次登录的用户导航到新页面时，Flask-Login会从会话中检索到用户的id,将用户加载到内存中
    '''
    return User.query.get(int(id))

from datetime import datetime
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(140))
    post_photo_url=db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index = True,default=datetime.now)
    '''将user.id字段初始化为外键user.id'''
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

