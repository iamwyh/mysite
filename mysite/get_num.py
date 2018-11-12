import pandas as pd
from datetime import datetime
from pyecharts import Bar,  Timeline, Line, Overlap
from django.db import connection as conn


citys = {
4:"深圳",
42:"广州",
53:"杭州",
85:"海口",
11:"上海",
201:"福州",
82:"珠海",
80:"惠州",
78:"东莞",
75:"成都",
66:"佛山",
205:"长沙",
206:"南京",
207:"武汉",
211:"重庆",
213:"厦门",
221:"肇庆",
222:"马鞍山",
223:"茂名",
224:"南通",
225:"南昌"
        }


weather = '''
SELECT date AS '日期', `day` AS '日间天气', `night` AS '夜间天气' FROM `weather` WHERE city = '{}'
'''

mob_shop = '''
SELECT c.pid, c.id, s.`online`, s.`status`, qy_time
FROM mob_shop s 
LEFT JOIN mob_pail p ON p.shop_id = s.id
INNER JOIN mob_city c ON c.id = s.city_id
WHERE s.is_del = 0 #未删除
AND s.cat_id != 73 #排除地推
AND s.cat_id != 74 #排除地推
AND s.shop_name NOT LIKE "%地推%"
AND s.shop_name NOT LIKE "%测试%"
AND s.shop_name NOT LIKE "%test%"
AND s.shop_name NOT LIKE "%拉新%"
AND (p.type != 1 or p.type is null)
'''


mob_site = '''
SELECT c.pid, c.id, s.`online`, s.`status`, s.qy_time
FROM mobrella_admin.mob_shop_site ss
LEFT JOIN mob_shop s ON ss.shop_id = s.id
LEFT JOIN mob_pail p ON ss.pail_id = p.id
INNER JOIN mob_city c ON c.id = s.city_id
WHERE s.is_del = 0 #未删除
AND s.cat_id != 73 #排除地推
AND s.cat_id != 74 #排除地推
AND s.shop_name NOT LIKE "%地推%"
AND s.shop_name NOT LIKE "%测试%"
AND s.shop_name NOT LIKE "%test%"
AND s.shop_name NOT LIKE "%拉新%"
AND (p.type != 1 or p.type is null)

'''


order_countJ = '''
SELECT DATE_FORMAT(o.borrow_time, "%Y-%m-%d") as '日期' , 
COUNT(1) AS '借伞订单',
COUNT(DISTINCT o.user_id) AS '借伞用户量',
COUNT(IF(o.`user_count`=1,1,NULL)) AS '首次借伞用户',
COUNT(DISTINCT o.pass_id) AS '有效伞桶'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
INNER JOIN mob_pail p ON p.id = o.pass_id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=date(o.borrow_time)
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
AND o.`status` in (1, 2)
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.borrow_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
AND (c.pid = {} or c.id = {}) # 城市
GROUP BY 日期
'''

order_countH = '''
SELECT DATE_FORMAT(o.finish_time, "%Y-%m-%d") as '日期' , 
COUNT(IF(o.`status`in (1, 2) AND o.is_resale=0,1,NULL)) AS '还伞订单',
SUM(IF(o.`status`=2 AND o.is_resale=0,payment_amount,NULL)) AS '借伞收入',
COUNT(IF(o.`status`=2 AND o.is_resale!=0,1,NULL)) AS '转售',
COUNT(IF(o.`status`=3,1,NULL)) AS '已取消'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
INNER JOIN mob_pail p ON p.id = o.pass_id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=date(o.finish_time)
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.finish_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
AND (c.pid = {} or c.id = {}) # 城市
GROUP BY 日期
'''

shop_order = '''
SELECT s.id AS 伞点编号, s.site_name AS 伞点名称, COUNT(1)
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
INNER JOIN mobrella_admin.mob_shop_site s ON o.pass_id = s.pail_id
INNER JOIN mob_pail p ON p.id = o.pass_id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=date(o.borrow_time)
AND o.user_id != '766921' # 排除测试
AND o.`status` in (1, 2)
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.borrow_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
AND (c.pid = {} or c.id = {}) # 城市
GROUP BY s.id
ORDER BY COUNT(1) DESC
'''
order_countJA = '''
SELECT DATE_FORMAT(o.borrow_time, "%Y-%m-%d") as '日期' , 
COUNT(1) AS '借伞订单',
COUNT(DISTINCT o.user_id) AS '借伞用户量',
COUNT(IF(o.`user_count`=1,1,NULL)) AS '首次借伞用户',
COUNT(DISTINCT o.pass_id) AS '有效伞桶'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
INNER JOIN mob_pail p ON p.id = o.pass_id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=date(o.borrow_time)
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
AND o.`status` in (1, 2)
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.borrow_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
GROUP BY 日期
'''

order_countHA = '''
SELECT DATE_FORMAT(o.finish_time, "%Y-%m-%d") as '日期' , 
COUNT(IF(o.`status`in (1, 2) AND o.is_resale=0,1,NULL)) AS '还伞订单',
SUM(IF(o.`status`=2 AND o.is_resale=0,payment_amount,NULL)) AS '借伞收入',
COUNT(IF(o.`status`=2 AND o.is_resale!=0,1,NULL)) AS '转售',
COUNT(IF(o.`status`=3,1,NULL)) AS '已取消'
FROM mob_order o
INNER JOIN mob_shop so ON o.borrow_shop_id = so.id
INNER JOIN mob_pail p ON p.id = o.pass_id
INNER JOIN mob_pail_kind k ON p.kind_id = k.id
INNER JOIN mob_shop_category sc ON sc.id = so.cat_id
INNER JOIN mob_city c ON c.id = so.city_id
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=date(o.finish_time)
AND o.user_id != '766921' # 排除测试
#AND o.from_type = 3 # 支付宝订单
AND so.cat_id != 73 # 排除地推商家
AND so.cat_id != 74 # 排除地推商家
#AND o.is_resale = 0 # 排除转售
#AND o.`status` = 2 # 已完结订单
AND so.`online` = 1 # 已上线的伞桶
AND so.is_del = 0 # 未删除的伞桶
AND DATE(o.finish_time) != CURDATE()
#AND p.type != 1
AND k.type_name NOT LIKE "%地推%"
AND k.type_name NOT LIKE "%测试%"
AND k.type_name NOT LIKE "%test%"
AND k.type_name NOT LIKE "%拉新%"
GROUP BY 日期
'''

new_users = '''
SELECT FROM_UNIXTIME(created_time, "%Y-%m-%d") AS '日期' ,
COUNT(1) AS '新增用户'
FROM mob_user 
WHERE DATE_SUB(CURDATE(), INTERVAL 7 DAY) <=DATE(FROM_UNIXTIME(created_time))
AND DATE(FROM_UNIXTIME(created_time)) != CURDATE()
GROUP BY 日期
'''

df = pd.DataFrame()
week_day_dict = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期天'}
df['日期'] = [datetime.strftime(x,'%Y-%m-%d') for x in list(pd.date_range(end=datetime.now(), periods=8, closed='left'))]
df['星期'] = [week_day_dict[y] for y in [x.weekday() for x in list(pd.date_range(end=datetime.now(), periods=8, closed='left'))]]
df_nuser = pd.read_sql(new_users,con=conn)


def order(df2,order_count_j,order_count_h,shop_order,*city):
    df_orderj = pd.read_sql(order_count_j.format(city[0],city[0]), con=conn) if city else pd.read_sql(order_count_j, con=conn)
    df_orderh = pd.read_sql(order_count_h.format(city[0],city[0]), con=conn) if city else pd.read_sql(order_count_h, con=conn)
    result = pd.merge(df_orderj,df_orderh,how='outer',on=['日期'])
    if result.size == 0:
        return None
    if not city:
        result = pd.merge(df_nuser,result,on='日期')
        result.sort_values('日期', inplace=True)
    df_order = pd.merge(df,result,how='outer',on='日期')
    df_order = df_order.fillna(0)
    try:
        city_shop = df2[df2['城市']==citys[city[0]]]['数量'].tolist()[0] if city else sum(df2['数量'])
    except IndexError:
        return None
    df_order[['借伞订单','借伞收入','借伞用户量','转售','已取消','有效伞桶']] = \
    df_order[['借伞订单','借伞收入','借伞用户量','转售','已取消','有效伞桶']].astype('int64')
    df_order['新用户率'] = df_order['首次借伞用户']/df_order['借伞用户量']
    df_order['新用户率'] = df_order['新用户率'].fillna(0).apply(lambda x: format(x, '.1%'))
    df_order['有效伞桶率'] = df_order['有效伞桶']/city_shop
    df_order['有效伞桶率'] = df_order['有效伞桶率'].apply(lambda x: format(x, '.1%'))
    df_order['借伞收入'] = df_order['借伞收入']/100
    df_order['平均每单收入'] = df_order['借伞收入']/df_order['还伞订单']
    df_order['单桶订单量'] = df_order['借伞订单']/city_shop
    df_order['单桶借伞用户量'] = df_order['借伞用户量']/city_shop
    df_order['单桶转售量'] = df_order['转售']/city_shop
    df_order['单桶取消量'] = df_order['已取消']/city_shop
    df_shop_order = pd.read_sql(shop_order.format(city[0],city[0]), con=conn) if shop_order else None
    df_order = df_order.fillna(0).round(2)
    df_order.sort_values('日期', inplace=True)
    return (df_order, df_shop_order) if city else df_order


def shops(x):
    df_mob_shop = pd.read_sql(x, con=conn)
    df_mob_shop['city_id'] = df_mob_shop['pid']
    df_mob_shop.loc[df_mob_shop['pid'] == 0,'city_id'] = df_mob_shop['id']
    def df(x, y):
        df = df_mob_shop[(df_mob_shop['online']==x)&(df_mob_shop['status']==y)].groupby(['city_id'])['city_id'].count().reset_index(name="数量")
        if x == 0:
            df = df_mob_shop[(df_mob_shop['online']==x)&(df_mob_shop['status']==y)&(df_mob_shop['qy_time'] > '2017-12-31')].groupby(['city_id'])['city_id'].count().reset_index(name="数量")
        df['城市'] = [citys[x] for x in df['city_id']]
        return df[['城市','数量']]
    return (df(0,2), df(1,2))

def out_bar(df,city):
    attr = [i for i in df['日期']]
    v1 = [i for i in df['借伞订单']]
    v11 = [i for i in df['还伞订单']]
    v2 = [i for i in df['借伞收入']]
    v3 = [i for i in df['借伞用户量']]
    v33 = [i for i in df['首次借伞用户']]
    v4 = [i for i in df['转售']]
    v5 = [i for i in df['已取消']]
    v6 = [i for i in df['有效伞桶']]
    v7 = [i for i in df['平均每单收入']]
    bar = Bar("{}近7日关键指标变化".format(city),title_text_size=16)
    bar.add("借伞订单", attr, v1,mark_line=["average"], mark_point=["max", "min"])
    bar.add("还伞订单", attr, v11,mark_line=["average"], mark_point=["max", "min"])
    bar.add("借伞收入", attr, v2,mark_line=["average"], mark_point=["max", "min"])
    bar.add("借伞用户量", attr, v3,mark_line=["average"], mark_point=["max", "min"])
    bar.add("首次借伞用户", attr, v33,mark_line=["average"], mark_point=["max", "min"])
    bar.add("转售", attr, v4,mark_line=["average"], mark_point=["max", "min"])
    bar.add("已取消", attr, v5,mark_line=["average"], mark_point=["max", "min"])
    bar.add("有效伞桶", attr, v6,mark_line=["average"], mark_point=["max", "min"],legend_pos='right',xaxis_name_size=6,xaxis_interval=0)
    line = Line()
    line.add("平均每单收入", attr, v7, yaxis_formatter=" 元",mark_line=["average"], mark_point=["max", "min"])
    overlap = Overlap()
    overlap.add(bar)
    overlap.add(line, yaxis_index=1, is_add_yaxis=True)
    return overlap

def get_pic():
    df2 =  shops(mob_site)[1]
    a = order(df2,order_countJA,order_countHA,'')
    sz = order(df2,order_countJ,order_countH,shop_order,4)[0]
    gz = order(df2,order_countJ,order_countH,shop_order,42)[0]
    hz = order(df2,order_countJ,order_countH,shop_order,53)[0]
    hk = order(df2,order_countJ,order_countH,shop_order,85)[0]
    sh = order(df2,order_countJ,order_countH,shop_order,11)[0]
    cs = order(df2,order_countJ,order_countH,shop_order,205)[0]
    fz = order(df2,order_countJ,order_countH,shop_order,201)[0]
    bar_a = out_bar(a,"全国")
    bar_sz  = out_bar(sz,"深圳")
    bar_gz  = out_bar(gz,"广州")
    bar_hz  = out_bar(hz,"杭州")
    bar_hk  = out_bar(hk,"海口")
    bar_sh  = out_bar(sh,"上海")
    bar_cs  = out_bar(cs,"长沙")
    bar_fz  = out_bar(fz,"福州")
    timeline = Timeline(is_auto_play=False, timeline_bottom=0, width=1100)
    timeline.add(bar_a, '全国')
    timeline.add(bar_sz, '深圳')
    timeline.add(bar_gz, '广州')
    timeline.add(bar_hz, '杭州')
    timeline.add(bar_hk, '海口')
    timeline.add(bar_sh, '上海')
    timeline.add(bar_cs, '长沙')
    timeline.add(bar_fz, '福州')
    return  timeline