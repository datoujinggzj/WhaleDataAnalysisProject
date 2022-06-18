# data processing
import pandas as pd
import numpy as np
from datetime import timedelta, datetime


# data visualization
import plotly.graph_objs as go
from plotly.graph_objs import Bar, Layout
from plotly import offline
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

# change text color
import colorama
from colorama import Fore, Style

def GET_csse_covid_19_time_series():


    print('正在读取【时间序列】数据......')
    repo = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'

    ts_confirmed_us = pd.read_csv(repo+'time_series_covid19_confirmed_US.csv')
    ts_confirmed_global = pd.read_csv(repo+'time_series_covid19_confirmed_global.csv')

    ts_deaths_us = pd.read_csv(repo+'time_series_covid19_deaths_US.csv')
    ts_deaths_global = pd.read_csv(repo+'time_series_covid19_deaths_global.csv')

    ts_recovered_global = pd.read_csv(repo+'time_series_covid19_recovered_global.csv')


    print('读取完毕')
    return ts_confirmed_us,ts_confirmed_global,ts_deaths_us,ts_deaths_global,ts_recovered_global



def GET_csse_covid_19_daily_reports():

    print('正在读取【横截面】数据......')

    # global
    ts_confirmed_us = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')

    latest = pd.to_datetime(ts_confirmed_us.columns[-1]).strftime('%m-%d-%Y')
    prev = (pd.to_datetime(ts_confirmed_us.columns[-1])+timedelta(-1)).strftime('%m-%d-%Y')

    url_latest_global = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{latest}.csv'
    latest_data_global = pd.read_csv(url_latest_global)

    url_prev_global = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{prev}.csv'
    prev_data_global = pd.read_csv(url_prev_global)

    url_latest_us = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/{latest}.csv'
    latest_data_us = pd.read_csv(url_latest_us)

    url_prev_us = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/{prev}.csv'
    prev_data_us = pd.read_csv(url_prev_us)


    print('读取完毕')
    return latest_data_global,prev_data_global,latest_data_us,prev_data_us

def GET_shanghai_data(data_name = 'ts_shanghai_covid', plot = False):
    
    '''
    data_name:数据名称：可选：'ts_shanghai_covid' 或者 'latest_shanghai_covid'，默认是'ts_shanghai_covid'
    plot：是否画图，默认是否
    '''
    import re
    print('正在获取并处理【上海】数据（数据来自上海卫健委）......')
    url = f'https://gitee.com/gzjzg/whale-pkg/raw/master/DATA/{data_name}.csv'
    data = pd.read_csv(url,encoding = 'gbk')['detail']
    print('读取完毕')
    
    data = data[data.apply(lambda x: x.startswith('上海202'))].sort_values()
    data = data.apply(lambda x: re.sub(r'\（.*?\）', '', x))
    data = data.apply(lambda x: x.replace('无新增','0'))
    
    df_all = pd.DataFrame(map(np.ravel,data.apply(lambda x: re.findall(r"\d+",x)))).rename({
    0:'年',
    1:'月',
    2:'日',
    3:'新增本土确诊',
    4:'新增本土无症状'
    },axis=1).iloc[:,:5]
    df_all['日期'] = df_all['年'].map(str)+"/"+df_all['月'].map(str)+"/"+df_all['日'].map(str)
    df_all['日期'] = pd.to_datetime(df_all['日期'])
    
    df_all = df_all.set_index('日期').sort_index()
    df_all = df_all.astype('int32')
    df = df_all.iloc[:,3:5]
    
    if plot:
        fig, axes = plt.subplots(nrows=2, ncols=1,figsize = [10,5*2])
        df_2022 = df[df.index>'2022-01-01']
        for col,ax in zip(df_2022.columns,axes):
            ax.step(df_2022.index, df_2022[col], color = '#202124',linewidth = 2)
            ax.bar(df_2022.index, df_2022[col],alpha = .8)
            ax.hlines(y=df[col].max(), xmin=df_2022.index[0], xmax=df_2022.index[-1], linewidth=1, color = '#ff0000')
            ax.text(x = df_2022.index[0], s=df[col].max(),y = df[col].max(), color = 'black', fontsize = 14)
            ax.text(x = df_2022.index[0], s=f"峰值：时间：{str(df.index[df['新增本土确诊'].argmax()])} 新增：{df[col].max()}例",y = df[col].max()/2, color = '#ff0000', fontsize = 18)
            ax.text(x = df_2022.index[0], s=f"今日：时间：{str(df.index[-1])} 新增：{df[col][-1]}例",y = df[col].max()/3, color = '#ff0000', fontsize = 18)
            ax.set_xlabel('日期')
            ax.set_ylabel(f'{col}数')
            ax.set_title(f'{col}时间序列趋势图',fontsize = 16)

        plt.tight_layout()
        
    return df