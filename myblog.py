'''从app模块中引用myapp应用'''
from app import myapp


'''防止被引用后执行，只有在当前模块中才可以使用'''
if __name__ == "__main__":
    '''运行myapp应用'''
    myapp.run(debug=True)