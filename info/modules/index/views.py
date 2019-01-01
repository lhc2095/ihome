from . import index_blue



#进入首页
@index_blue.route('/')
def index():
    from manage import app
    return app.send_static_file('index.html')
