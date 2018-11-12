from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response
from books.models import Publisher
from django.http import HttpResponse
from django.db import connection
import pandas as pd
import datetime
from .get_num import get_pic

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
	

	
def index(request):
    # 可视化展示页面
    bar = get_pic()
    myechart = bar.render_embed()  # 图
    host=REMOTE_HOST  # js文件源地址
    script_list=bar.get_js_dependencies()  # 获取依赖的js文件名称（只获取当前视图需要的js）
    return render_to_response('index.html', locals())
