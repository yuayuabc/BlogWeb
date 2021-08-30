'''从app包中导入数据库实例db'''
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

