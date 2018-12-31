from . import index_blue

from flask import  render_template

@index_blue.route('/')
def index():
    return render_template('html/test.html')