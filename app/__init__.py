'''
模块初始化文件
用于创建程序的对象，子目录app可作为包被引用
'''

from flask import Flask

'''
myapp应用程序实例
__name__传递给Flask类的变量是Python预定义变量，该变量设置为使用该变量的模块的名称
'''

'''pip install bootstrap-flask'''
from flask_bootstrap import Bootstrap

myapp = Flask(__name__)

'''从config模块引用Config类,导入配置文件'''
from config import Config
'''为myapp应用程序添加配置信息'''
myapp.config.from_object(Config)

from flask_uploads import UploadSet,configure_uploads,patch_request_class

'''配置上传集 photo ,设置上传类型为PNG,png,jpeg'''
photo = UploadSet('photos',['PNG','png','jpeg','jpg'])
configure_uploads(myapp,photo)
patch_request_class(myapp,size=None)




'''
pip install flask-sqlalchemy
pip install flask-migrate
pip install psycopg2
'''
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

'''创建myapp应用程序的数据库实例'''
db = SQLAlchemy(myapp)

'''创建数据库db和应用程序myapp的迁移引擎实例'''
migrate = Migrate(myapp,db)


'''pip install flask-login下载Flask扩展，导入LoginManager函数
   此扩展能管理用户的登录状态，提供“记住我”功能，使用户能保持登录状态
'''
from flask_login import LoginManager

'''创建并初始化Flask-Login为login'''
'''login的创建需在数据库实例和迁移引擎创建之后，models，routes导入之前'''
login = LoginManager(myapp)


'''等式右边的'login'是登录视图的函数（或端点）名称，在url_for()调用中用于获取 URL。
   Flask-Login保护视图函数免受匿名用户攻击的方法是：
      使用@login_required装饰器，添加到Flask的@myapp.route装饰器下方，视图函数受到保护，并不允许未经身份验证的用户访问。
'''
login.login_view = 'login'


bootstrap = Bootstrap(myapp)


'''myapp应用程序从app包中引用routes模块'''
from app import routes,models
from app import errors


