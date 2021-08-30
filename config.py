import os

'''获取当前路径'''
basedir = os.path.abspath(os.path.dirname(__file__))

'''创建类Config来存储配置变量'''
class Config(object):

    '''
    为了确保表单提交过来的是安全的，所以我们设定一个安全钥匙SECRET_KEY。
    当用户请求表单时，将这个钥匙给用户，
    然后用户提交表单的时候，将这个钥匙和我们服务器中的钥匙比对一下，
    如果安全的话就接收用户表单里的信息，
    如果比对不成功，那说明这个用户提交过来的数据有问题
    '''
    '''
    查看方法：python
    from myblog import myapp
    myapp.config['SECRET_KEY']
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    '''获取应用程序中数据库的位置'''
    SQLALCHEMY_DATABASE_URI = 'postgresql://fight:123456@localhost:5432/fightDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    '''上传路径配置'''
    UPLOADS_DEFAULT_DEST = os.path.join(basedir,'static')
    MAX_CONTENT_LENGTH = 1024*1024*64

    FLASK_ADMIN_SWATCH = 'cerulean'
    