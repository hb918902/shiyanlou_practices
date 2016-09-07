#! usr/bin/python3
# coding:utf-8

"""
Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达


Example:
    tickets 北京 上海 2016-08-25
"""


from docopt import docopt
from prettytable import PrettyTable
import requests
import re


def cre_stations():
    url_sta = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8955'
    sta = requests.get(url_sta,verify=False)
    # create stations dict
    sta_list = [station.split('|') for station in sta.text.split('@')[1:]]
    stations = {station[1]: station[2] for station in sta_list}
    return stations


def colored(color,text):
    table = {
        'red': '\033[91m',
        'green': '\033[92m',
        'nocolor': '\033[0m'
    }
    cv = table.get(color)
    nc = table.get('nocolor')
    return ''.join([cv,text,nc])


class TrainCollection(object):
    # 显示车次、出发/到达站、 出发/到达时间、历时、商务座、特等座、一等坐、二等坐、软卧、硬卧、硬座
    header = '车次 出发/到达站 出发/到达时间 历时 商务座 特等座 一等座 二等座 软卧 硬卧 硬座 无座'.split()

    def __init__(self, rows):
        self.rows = rows

    def _get_duration(self,row):
        """
        获取车次运行时间
        """
        duration = row.get('lishi').replace(':', 'h') + 'm'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for row in self.rows:
            train = [
                # 车次
                row['station_train_code'],
                # 出发、到达站
                '\n'.join([colored('green', row['from_station_name']),colored('red', row['to_station_name'])]),
                # 出发、到达时间
                '\n'.join([colored('green', row['start_time']),colored('red', row['arrive_time'])]),
                # 历时
                self._get_duration(row),
                # 商务座
                row['swz_num'],
                # 特等座
                row['tz_num'],
                # 一等坐
                row['zy_num'],
                # 二等坐
                row['ze_num'],
                # 软卧
                row['rw_num'],
                # 软坐
                row['yw_num'],
                # 硬坐
                row['yz_num'],
                # 无座
                row['wz_num']
            ]
            yield train

    def pretty_print(self):
        """
        数据已经获取到了，剩下的就是提取我们要的信息并将它显示出来。
        `prettytable`这个库可以让我们它像MySQL数据库那样格式化显示数据。
        """
        pt = PrettyTable()
        # 设置每一列的标题
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


def cli():
    """command-line interface"""
    arguments = docopt(__doc__)
    from_station = cre_stations().get(arguments['<from>'])
    to_station = cre_stations().get(arguments['<to>'])
    date = arguments['<date>']
    gaotie = arguments['-g']
    dongche = arguments['-d']
    tekuai = arguments['-t']
    kuaiche = arguments['-k']
    zhida = arguments['-z']
    commandflag = ''
    if gaotie:
        commandflag += 'G'
    if dongche:
        commandflag += 'D'
    if tekuai:
        commandflag += 'T'
    if kuaiche:
        commandflag += 'K'
    if zhida:
        commandflag += 'Z'
    # create URL
    url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(
        date, from_station, to_station)
    r = requests.get(url,verify=False)
    try:
        rows = r.json()['data']['datas']
        if commandflag:
            rows = filter(lambda x:re.match(commandflag,x['station_train_code']),rows)
        trains = TrainCollection(rows)
        trains.pretty_print()
    except ValueError:
        print("服务器错误，请重试！")
    except TypeError:
        print("输入错误，请重试")
    except KeyError:
        print("没有符合条件的数据")


if __name__ == '__main__':
    cli()
