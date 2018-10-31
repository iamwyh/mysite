from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response
from books.models import Publisher
from django.http import HttpResponse
from pyecharts import Pie
from django.db import connection
import pandas as pd
import datetime

REMOTE_HOST = "https://pyecharts.github.io/assets/js"

def hello(request):
    return HttpResponse("Hello world")

def current_datetime(request):
    current_date = datetime.datetime.now()
    return render_to_response('current_datetime.html', locals())

def hours_ahead(request, offset):
    try:
        hour_offset = int(offset)
    except ValueError:
        raise Http404()
    next_time = datetime.datetime.now() + datetime.timedelta(hours=hour_offset)
    return render_to_response('hours_ahead.html', locals())

def test_model(request):
    pu = Publisher.objects.all()
    return render_to_response('test_model.html', locals())
	

def Pie_():
    # 生成饼图
    sql = 'SELECT `name`, COUNT(1) FROM `books_publisher` GROUP BY `name`'
    df = pd.read_sql(sql, con=connection)
    attr = [i for i in df['name']]
    v = [i for i in df['COUNT(1)']]
    pie = Pie("饼图示例")
    pie.add("", attr, v, is_label_show=True) 
    return pie
	
def index(request):
    # 可视化展示页面
    pie = Pie_()
    myechart=pie.render_embed() # 饼图
    host=REMOTE_HOST # js文件源地址
    script_list=pie.get_js_dependencies() # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_to_response('index.html', locals())