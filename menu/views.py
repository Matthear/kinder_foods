from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import json
from datetime import datetime, timezone, timedelta
from collections import OrderedDict
import pymysql.cursors

# Create your views here.
def ajax(request):
    if request.method == 'POST':
        # 获取页面请求的日期，如果没有，则默认为当前日期（UTC+8）
        # 页面时区以浏览器自动调整
        query_date = request.POST.get('query_date', datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d'))
        query_date_menu = db_query(query_date)
        for k, v in query_date_menu.items():
            date_in_subquery = k
            menu = v
        if menu:
            menu_sort = sort(menu)
            query_date_menu[date_in_subquery] = menu_sort
        data = json.dumps(query_date_menu) # 如果没有查询到相应日期的菜单, menu==None -> data==null 
        return HttpResponse(data, content_type='application/json')
    
def show_menu(request):
    return render(request, 'menu.html')
    
def db_query(query_date):
    # 前端和python的日期格式有略微差异，统一格式
    year_month_day = query_date.split('-')
    year = int(year_month_day[0])
    month = int(year_month_day[1])
    day = int(year_month_day[2])
    date_in_subquery = datetime(year, month, day).strftime('%Y-%m-%d')
    
    # 查询数据库
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='ZJZAnAn4ever',
                                db='test',
                                charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT * FROM test.kinder_foods where week=(SELECT week FROM test.kinder_foods where date="''' + date_in_subquery + '''" LIMIT 1) order by `date`, `diet`, `comment` desc'''
            print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
            #print(result)
    finally:
        connection.close()
    
    # 没有结果的情况
    if len(result) == 0:
        return {date_in_subquery: None}
    
    # 查询成功有结果的情况
    # 数据结构：{query_date: {date1: { 'diet1': 'food1<br><food2>', 'diet2': 'food3<br>food4', 'diet3': 'food5<br>food6' } },
    #                        {date2: { 'diet1': 'food1<br><food2>', 'diet2': 'food3<br>food4', 'diet3': 'food5<br>food6' } },
    #                        ...
    #                        {date5: { 'diet1': 'food1<br><food2>', 'diet2': 'food3<br>food4', 'diet3': 'food5<br>food6' } }}
    week = result[0]['week']
    menu = {}
    for row in result:
        date = row['date'].strftime('%Y-%m-%d')
        diet = row['diet']
        food = row['food']
        comment = row['comment']
        
        if len(menu) == 0 or date != last_date:
    #         初始化某日期（date）的菜单（menu）
            menu[date] = {diet: food} if comment == '' else {diet: food + '（' + comment + '）'}
        else:
            if diet in menu[date].keys():
    #             更新某餐点（diet）的菜品（food）
                menu[date][diet] = menu[date][diet] + '<br>' + food if comment == '' else \
                menu[date][diet] + '<br>' + food + '（' + comment + '）'
            else:
    #             第一次添加某餐点的菜品
                menu[date][diet] = food if comment == '' else food + '（' + comment + '）'
        
        last_date = date
    
    return {date_in_subquery: menu}

def sort(menu):
    key_order = ['早点', '午餐', '午点', '体弱儿营养菜']
    menu_sort = {}
    for date, meals in menu.items():
        meals_sort = OrderedDict()
        for meal in key_order:
            meals_sort[meal] = meals[meal]
        menu_sort[date] = meals_sort
    return menu_sort