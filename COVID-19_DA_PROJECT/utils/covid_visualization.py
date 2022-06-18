# data processing
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import re

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


def Decompose_CHINA(ts_data_processed,
                    latest_data_processed,
                    prev_data_processed,
                    start=None,
                    end=None,
                    ma = None,
                    method = '新增',
                    specify = None,
                    verbose = 1,
                    kind = '确诊'):

    ts_copy = ts_data_processed.copy()

    district = latest_data_processed.index.to_list()
    # cases
    cum_cases_total = ts_data_processed.sum(axis=1).sum()
    incre_cases_total = ts_data_processed.sum(axis=1)[-1]

    # deaths
    cum_deaths_total = latest_data_processed['Deaths'].sum()
    incre_deaths_total = (latest_data_processed['Deaths']- prev_data_processed['Deaths']).sum()

    if specify is not None and specify != 'All':
        cum_cases_district_total =ts_data_processed[specify].sum().astype('int32')
        incre_cases_district_total = ts_data_processed[specify][-1].astype('int32')

        cum_deaths_district_total = latest_data_processed.loc[specify,'Deaths']
        incre_deaths_district_total = latest_data_processed.loc[specify,'Deaths'] - prev_data_processed.loc[specify,'Deaths']

    # last_update date
    last_update = latest_data_processed['Last_Update'].unique()[0]

    cum_deaths_total = latest_data_processed['Deaths'].sum()
    incre_deaths_total = (latest_data_processed['Deaths']- prev_data_processed['Deaths']).sum()

    print("国家：中国")
    print(f"最新更新时间：{last_update}")
    print('-'*40 + 'TOTAL' + '-'*41)
    print(f"截至目前【中国】累计确诊：{Fore.BLUE}{int(cum_cases_total)}{Style.RESET_ALL} | 新增确诊：{Fore.BLUE}{int(incre_cases_total)}{Style.RESET_ALL}\n"
          f"截至目前【中国】累计死亡：{Fore.RED}{cum_deaths_total}{Style.RESET_ALL} | 新增死亡：{Fore.RED}{incre_deaths_total}{Style.RESET_ALL}")
    if specify is not None and specify != 'All':
        print(f"截至目前【{specify}】累计确诊：{Fore.BLUE}{cum_cases_district_total}{Style.RESET_ALL} | 新增确诊：{Fore.BLUE}{incre_cases_district_total}{Style.RESET_ALL}\n"
              f"截至目前【{specify}】累计死亡：{Fore.RED}{cum_deaths_district_total}{Style.RESET_ALL} | 新增死亡：{Fore.RED}{incre_deaths_district_total}{Style.RESET_ALL}")
    print('-'*40 + 'DETAIL' + '-'*40)
    print(f"{Fore.BLUE}蓝色{Style.RESET_ALL}为确诊数\n{Fore.RED}红色{Style.RESET_ALL}为死亡数")
    print('-'*86)
    if verbose == 0:
        from tabulate import tabulate
        if method == '新增':
            print(tabulate(sorted(zip(district,
                                      ts_data_processed.tail(1).T.reindex(latest_data_processed.index).values,
                                      latest_data_processed['Deaths']- prev_data_processed['Deaths'],
                                      latest_data_processed['Incident_Rate'],
                                      latest_data_processed['Case_Fatality_Ratio']),
                                  key = lambda x: x[1],reverse=True),
                           headers=["省级行政区", "新增确诊数↓", "新增死亡数", "每10万人确诊人数","累计致死率（%）"],
                           tablefmt="psql"))
        elif method == '累计':
            print(tabulate(sorted(zip(district,
                                      ts_data_processed.sum(),
                                      latest_data_processed['Deaths'],
                                      latest_data_processed['Incident_Rate'],
                                      latest_data_processed['Case_Fatality_Ratio']),
                                  key = lambda x: x[4],reverse=True),
                           headers=["省级行政区", f"{method}确诊数", f"{method}死亡数", "每10万人确诊人数","累计致死率（%）↓"],
                           tablefmt="psql"))
    if verbose == 1:
        if method == '新增':
            print("{:<25} {:<10} {:<10} {:<10} {:<10}".format('省级行政区',
                                                              f'{method}确诊数↓',
                                                              f'{method}死亡数',
                                                              '每10万人确诊人数',
                                                              '累计致死率'))
            for province, case, death, incident_rate, case_fatality_ratio in sorted(zip(district,
                                                                                        ts_data_processed.tail(1).T.reindex(latest_data_processed.index).values,
                                                                                        latest_data_processed['Deaths']- prev_data_processed['Deaths'],
                                                                                        latest_data_processed['Incident_Rate'],
                                                                                        latest_data_processed['Case_Fatality_Ratio']),
                                                                                    key = lambda x: x[1],reverse=True):
                print("{:<30} {:<25} {:<23} {:<26} {:<23}".format(province,
                                                                  f"{Fore.BLUE}{int(case[0])}{Style.RESET_ALL}",
                                                                  f"{Fore.RED}{death}{Style.RESET_ALL}",
                                                                  f"{Fore.GREEN}{round(incident_rate,3)}{Style.RESET_ALL}",
                                                                  f"{Fore.LIGHTYELLOW_EX}{round(case_fatality_ratio,3)}%{Style.RESET_ALL}"
                                                                  ))
        elif method == '累计':
            print("{:<25} {:<10} {:<10} {:<10} {:<10}".format('省级行政区',
                                                              f'{method}确诊数',
                                                              f'{method}死亡数',
                                                              '每10万人确诊人数',
                                                              '累计致死率↓'))
            for province, case, death, incident_rate, case_fatality_ratio in sorted(zip(district,
                                                                                        #latest_data_processed['Confirmed'],
                                                                                        ts_data_processed.sum().reindex(latest_data_processed.index),
                                                                                        latest_data_processed['Deaths'],
                                                                                        latest_data_processed['Incident_Rate'],
                                                                                        latest_data_processed['Case_Fatality_Ratio']),
                                                                                    key = lambda x: x[4],reverse=True):
                #print(province, f"{Fore.BLUE}{case}{Style.RESET_ALL}",f"{Fore.RED}{death}{Style.RESET_ALL}")
                print("{:<30} {:<25} {:<23} {:<26} {:<23}".format(province,
                                                                  f"{Fore.BLUE}{int(case)}{Style.RESET_ALL}",
                                                                  f"{Fore.RED}{death}{Style.RESET_ALL}",
                                                                  f"{Fore.GREEN}{round(incident_rate,3)}{Style.RESET_ALL}",
                                                                  f"{Fore.LIGHTYELLOW_EX}{round(case_fatality_ratio,3)}%{Style.RESET_ALL}"
                                                                  ))
    ###############################################################################################################################
    if method == '新增':
        data = ts_data_processed
    elif method == '累计':
        data = ts_data_processed.cumsum()
    if start is not None:
        data = data[data.index>=start]
    if end is not None:
        data = data[data.index<=end]
    if (start is not None) and (end is not None):
        data = data[(data.index>=start) & (data.index<=end)]
    if end is not None:
        data = data[data.index<=end]
        # print(data)
    # loop through tickers and axes
    # filter df for ticker and plot on specified axes
    if specify is not None:
        idx = data.index
        if specify != 'All':
            ser = data[specify]
            layout_title = specify.upper()
        else:
            ser = data.drop(['Tibet','Hong Kong'],axis=1).sum(axis=1)
            layout_title = '中国大陆'
        trace = go.Scatter(
            x = idx,
            y = ser,
            mode = 'lines+markers',
            name = f'{method}{kind}数',
            opacity = .8,
            line=dict(color="#08a8c4",width = .4),
            marker = dict(color = '#5857e1',size = 1.2)
        )
        trace1 = go.Scatter(
            x = idx,
            y = ser.rolling(ma[0]).mean(),
            mode = 'lines+markers',
            name = f'{ma[0]}天移动平均',
            opacity = .6,
            line=dict(color="#ee5090",width = 1.4),
            marker = dict(color = '#dd001b',size = 2.2)
        )
        trace2 = go.Scatter(
            x = idx,
            y = ser.rolling(ma[1]).mean(),
            mode = 'lines+markers',
            name = f'{ma[1]}天移动平均',
            opacity = .8,
            line=dict(color="#006eff",width = 2.4),
            marker = dict(color = '#412b63',size = 3.2)
        )


        plotdata = [trace,trace1,trace2]

        '''启动绘图'''

        x_axis_config = {'title': '日期'}
        y_axis_config = {'title': f'{kind}数（{method.upper()}）'}
        # 返回指定的图像布局和配置对象
        my_layout = Layout(title=f"【{layout_title}】近日【{kind}】数时间序列折线图（{method.upper()}）",
                           xaxis=x_axis_config, yaxis=y_axis_config)
        # 生成图表
        offline.iplot({'data': plotdata, 'layout': my_layout}, filename=f'{layout_title}_COVID_TS',image_height=500,image_width=1000,image = 'png')

    else:

        data_copy = data.copy()
        data = data.drop(['Tibet'],axis=1).sort_values(axis=1, by =data.index[-1],ascending=False)
        plt.style.use('ggplot')
        fig, axs = plt.subplots(nrows=8, ncols=4, figsize=(15*4, 10*8))
        plt.subplots_adjust(hspace=0.5)
        plt.suptitle("中国各省疫情趋势图", fontsize=50, y = 0.9)
        for province,ax in zip(data.columns, axs.ravel()):
            #ax.set_ylim([0, 500])
            data[province].plot(ax=ax,rot = 30, fontsize = 12,alpha = .3, label = method, color = '#06c3cc')
            if ma is not None:
                data[province].rolling(ma[0]).mean().plot(ax=ax,rot = 30, fontsize = 12,label = f'ma{ma[0]}',color = 'red')
                data[province].rolling(ma[1]).mean().plot(ax=ax,rot = 30, fontsize = 12,label = f'ma{ma[1]}',color = 'blue')
            ax.set_title(f"{province.upper()}今日新增{kind}：{int(ts_copy[province].tail(1))}例",fontsize = 25)
            ax.legend(fontsize = 15)
            ax.set_xlabel("")
        plt.show()



def Decompose_US(ts_data_processed,
                 latest_data_processed,
                 prev_data_processed,
                 start=None,
                 end=None,
                 ma = None,
                 method = '新增',
                 specify = None,
                 verbose = 1,
                 kind = '确诊'):

    ts_copy = ts_data_processed.copy()

    district = latest_data_processed.index.to_list()
    # cases

    cum_cases_total = latest_data_processed['Confirmed'].sum()
    incre_cases_total = latest_data_processed['Confirmed'].sum()-prev_data_processed['Confirmed'].sum()


    # deaths
    cum_deaths_total = latest_data_processed['Deaths'].sum()
    incre_deaths_total = (latest_data_processed['Deaths']- prev_data_processed['Deaths']).sum()

    if specify is not None and specify != 'All':
        cum_cases_district_total = latest_data_processed.loc[specify,'Confirmed']
        incre_cases_district_total = latest_data_processed.loc[specify,'Confirmed'] - prev_data_processed.loc[specify,'Confirmed']

        cum_deaths_district_total = latest_data_processed.loc[specify,'Deaths']
        incre_deaths_district_total = latest_data_processed.loc[specify,'Deaths'] - prev_data_processed.loc[specify,'Deaths']

    # last_update date
    last_update = latest_data_processed['Last_Update'].unique()[0]

    cum_deaths_total = latest_data_processed['Deaths'].sum()
    incre_deaths_total = (latest_data_processed['Deaths']- prev_data_processed['Deaths']).sum()

    print("国家：美国")
    print(f"最新更新时间：{last_update}")
    print('-'*40 + 'TOTAL' + '-'*41)
    print(f"截至目前【美国】累计确诊：{Fore.BLUE}{cum_cases_total}{Style.RESET_ALL} | 新增确诊：{Fore.BLUE}{incre_cases_total}{Style.RESET_ALL}\n"
          f"截至目前【美国】累计死亡：{Fore.RED}{cum_deaths_total}{Style.RESET_ALL} | 新增死亡：{Fore.RED}{incre_deaths_total}{Style.RESET_ALL}")
    if specify is not None and specify != 'All':
        print(f"截至目前【{specify}】累计确诊：{Fore.BLUE}{cum_cases_district_total}{Style.RESET_ALL} | 新增确诊：{Fore.BLUE}{incre_cases_district_total}{Style.RESET_ALL}\n"
              f"截至目前【{specify}】累计死亡：{Fore.RED}{cum_deaths_district_total}{Style.RESET_ALL} | 新增死亡：{Fore.RED}{incre_deaths_district_total}{Style.RESET_ALL}")
    print('-'*40 + 'DETAIL' + '-'*40)
    print(f"{Fore.BLUE}蓝色{Style.RESET_ALL}为确诊数\n{Fore.RED}红色{Style.RESET_ALL}为死亡数")
    print('-'*86)
    if verbose == 0:
        from tabulate import tabulate
        if method == '新增':
            print(tabulate(sorted(zip(district,
                                      latest_data_processed['Confirmed']- prev_data_processed['Confirmed'],
                                      latest_data_processed['Deaths']- prev_data_processed['Deaths'],
                                      latest_data_processed['Incident_Rate'],
                                      latest_data_processed['Case_Fatality_Ratio']),
                                  key = lambda x: x[1],reverse=True),
                           headers=["省级行政区", "新增确诊数↓", "新增死亡数", "每10万人确诊人数","累计致死率（%）"],
                           tablefmt="psql"))
        elif method == '累计':
            print(tabulate(sorted(zip(district,
                                      latest_data_processed['Confirmed'],
                                      latest_data_processed['Deaths'],
                                      latest_data_processed['Incident_Rate'],
                                      latest_data_processed['Case_Fatality_Ratio']),
                                  key = lambda x: x[4],reverse=True),
                           headers=["省级行政区", f"{method}确诊数", f"{method}死亡数", "每10万人确诊人数","累计致死率（%）↓"],
                           tablefmt="psql"))
    if verbose == 1:
        if method == '新增':
            print("{:<25} {:<10} {:<10} {:<10} {:<10}".format('省级行政区',
                                                              f'{method}确诊数↓',
                                                              f'{method}死亡数',
                                                              '每10万人确诊人数',
                                                              '累计致死率'))
            for province, case, death, incident_rate, case_fatality_ratio in sorted(zip(district,
                                                                                        #  (latest_data_processed['Confirmed']- prev_data_processed['Confirmed']).clip(lower=0),
                                                                                        #  (latest_data_processed['Deaths']- prev_data_processed['Deaths']).clip(lower=0),
                                                                                        #latest_data_processed['Confirmed']- prev_data_processed['Confirmed'],
                                                                                        latest_data_processed['Confirmed']- prev_data_processed['Confirmed'],
                                                                                        latest_data_processed['Deaths']- prev_data_processed['Deaths'],
                                                                                        latest_data_processed['Incident_Rate'],
                                                                                        latest_data_processed['Case_Fatality_Ratio']),
                                                                                    key = lambda x: x[1],reverse=True):
                #print(province, f"{Fore.BLUE}{case}{Style.RESET_ALL}",f"{Fore.RED}{death}{Style.RESET_ALL}")
                print("{:<30} {:<25} {:<23} {:<26} {:<23}".format(province,
                                                                  f"{Fore.BLUE}{case}{Style.RESET_ALL}",
                                                                  f"{Fore.RED}{death}{Style.RESET_ALL}",
                                                                  f"{Fore.GREEN}{round(incident_rate,3)}{Style.RESET_ALL}",
                                                                  f"{Fore.LIGHTYELLOW_EX}{round(case_fatality_ratio,3)}%{Style.RESET_ALL}"
                                                                  ))
        elif method == '累计':
            print("{:<25} {:<10} {:<10} {:<10} {:<10}".format('省级行政区',
                                                              f'{method}确诊数',
                                                              f'{method}死亡数',
                                                              '每10万人确诊人数',
                                                              '累计致死率↓'))
            for province, case, death, incident_rate, case_fatality_ratio in sorted(zip(district,
                                                                                        #latest_data_processed['Confirmed'],
                                                                                        latest_data_processed['Confirmed'],
                                                                                        latest_data_processed['Deaths'],
                                                                                        latest_data_processed['Incident_Rate'],
                                                                                        latest_data_processed['Case_Fatality_Ratio']),
                                                                                    key = lambda x: x[4],reverse=True):
                #print(province, f"{Fore.BLUE}{case}{Style.RESET_ALL}",f"{Fore.RED}{death}{Style.RESET_ALL}")
                print("{:<30} {:<25} {:<23} {:<26} {:<23}".format(province,
                                                                  f"{Fore.BLUE}{int(case)}{Style.RESET_ALL}",
                                                                  f"{Fore.RED}{death}{Style.RESET_ALL}",
                                                                  f"{Fore.GREEN}{round(incident_rate,3)}{Style.RESET_ALL}",
                                                                  f"{Fore.LIGHTYELLOW_EX}{round(case_fatality_ratio,3)}%{Style.RESET_ALL}"
                                                                  ))
    ###############################################################################################################################
    if method == '新增':
        data = ts_data_processed
    elif method == '累计':
        data = ts_data_processed.cumsum()
    if start is not None:
        data = data[data.index>=start]
    if end is not None:
        data = data[data.index<=end]
    if (start is not None) and (end is not None):
        data = data[(data.index>=start) & (data.index<=end)]
    if end is not None:
        data = data[data.index<=end]
        # print(data)
    # loop through tickers and axes
    # filter df for ticker and plot on specified axes
    if specify is not None:
        idx = data.index
        if specify != 'All':
            ser = data[specify]
            layout_title = specify.upper()
        else:
            ser = data.sum(axis=1)
            layout_title = '美国'
        trace = go.Scatter(
            x = idx,
            y = ser,
            mode = 'lines+markers',
            name = f'{method}{kind}数',
            opacity = .8,
            line=dict(color="#08a8c4",width = .4),
            marker = dict(color = '#5857e1',size = 1.2)
        )
        trace1 = go.Scatter(
            x = idx,
            y = ser.rolling(ma[0]).mean(),
            mode = 'lines+markers',
            name = f'{ma[0]}天移动平均',
            opacity = .6,
            line=dict(color="#ee5090",width = 1.4),
            marker = dict(color = '#dd001b',size = 2.2)
        )
        trace2 = go.Scatter(
            x = idx,
            y = ser.rolling(ma[1]).mean(),
            mode = 'lines+markers',
            name = f'{ma[1]}天移动平均',
            opacity = .8,
            line=dict(color="#006eff",width = 2.4),
            marker = dict(color = '#412b63',size = 3.2)
        )


        plotdata = [trace,trace1,trace2]

        '''启动绘图'''

        x_axis_config = {'title': '日期'}
        y_axis_config = {'title': f'{kind}数（{method.upper()}）'}
        # 返回指定的图像布局和配置对象
        my_layout = Layout(title=f"【{layout_title}】近日【{kind}】数时间序列折线图（{method.upper()}）",
                           xaxis=x_axis_config, yaxis=y_axis_config)
        # 生成图表
        offline.iplot({'data': plotdata, 'layout': my_layout}, filename=f'{layout_title}_COVID_TS',image_height=500,image_width=1000,image = 'png')

    else:

        data_copy = data.copy()
        plt.style.use('ggplot')
        fig, axs = plt.subplots(nrows=13, ncols=4, figsize=(15*4, 10*13))
        plt.subplots_adjust(hspace=0.5)
        plt.suptitle(f"美国各州疫情趋势图", fontsize=50, y = 0.9)
        for province,ax in zip(data.columns, axs.ravel()):
            #ax.set_ylim([0, 500])
            data[province].plot(ax=ax,rot = 30, fontsize = 12,alpha = .3, label = method, color = '#06c3cc')
            if ma is not None:
                data[province].rolling(ma[0]).mean().plot(ax=ax,rot = 30, fontsize = 12,label = f'ma{ma[0]}',color = 'red')
                data[province].rolling(ma[1]).mean().plot(ax=ax,rot = 30, fontsize = 12,label = f'ma{ma[1]}',color = 'blue')
            ax.set_title(f"{province.upper()}今日新增{kind}：{int(ts_copy[province].tail(1))}例",fontsize = 25)
            ax.legend(fontsize = 15)
            ax.set_xlabel("")
        plt.show()