from enum import Enum, unique, auto
import sys
import os
import csv


@unique
class State(Enum):
    Before = 1
    Labeling = auto()
    Exploring = auto()
    Processing = auto()
    End = auto()


@unique
class DataType(Enum):
    Continuous = auto()
    Discreate = auto()


class Data:
    pass


def trim(string):
    string = string.strip()
    string = string.replace(' ', '')
    string = string.replace('	', '')  # 半角でも全角でもない謎の空白文字を除去
    return string


def create_dict_list(filename, data_count):
    res = []
    f = open('txt/' + filename + '.txt', 'r')
    state = State.Before
    line = f.readline()
    data = Data()

    while line:
        line = trim(line)
        if (not len(line)):
            line = f.readline()
            continue

        if (line.startswith('一変量の分布')):
            line = line.split('一変量の分布')[1]
            if (line):
                data = Data()
                data.label = line
                res.append(data_to_dict(data))
            state = State.Labeling
            line = f.readline()
            continue

        if (state == State.Labeling):
            data = Data()
            data.label = line
            state = State.Exploring
            line = f.readline()
            continue

        if (state == State.Exploring):
            if (line not in ['度数', '分位点']):
                raise RuntimeError()
            if (line == '度数'):
                data.type = DataType.Discreate
            if (line == '分位点'):
                data.type = DataType.Continuous
            state = State.Processing
            line = f.readline()
            continue

        if (state == State.Processing):
            while not (line.startswith('N') or line.endswith('水準')):
                if (line == '水準度数割合'):
                    line = f.readline()
                    line = trim(line)
                    while not line.startswith('合計'):
                        if (line.startswith('0')):
                            line = line[1:]
                            line = line.split('.')[0]
                            line = line[:-1]
                            data.zero = line
                            line = f.readline()
                            line = trim(line)
                            continue
                        if (line.startswith('1')):
                            line = line[1:]
                            line = line.split('.')[0]
                            line = line[:-1]
                            data.one = line
                            line = f.readline()
                            line = trim(line)
                            continue
                        if (hasattr(data, 'special')):
                            data.special += line
                        else:
                            data.special = line
                        line = f.readline()
                        line = trim(line)
                if (line.startswith('欠測値N')):
                    data.missing = line.split('欠測値N')[1]
                if (line.startswith('75.0%四分位点')):
                    data.third_quartile = line.split('75.0%四分位点')[1]
                if (line.startswith('50.0%中央値')):
                    data.median = line.split('50.0%中央値')[1]
                if (line.startswith('25.0%四分位点')):
                    data.first_quartile = line.split('25.0%四分位点')[1]
                if (line.startswith('平均の下側95%')):
                    line = f.readline()
                    line = trim(line)
                    data.missing = data_count - int(line.split('N')[1])
                    continue
                line = f.readline()
                line = trim(line)
            res.append(data_to_dict(data))
            state = State.Labeling
            line = f.readline()
            continue
        line = f.readline()
    f.close()
    return res


def data_to_dict(data):
    res = dict()
    res['ラベル'] = data.label
    res['欠損数'] = data.missing if hasattr(data, 'missing') else ''
    res['0'] = data.zero if hasattr(data, 'zero') else ''
    res['1'] = data.one if (hasattr(data, 'one')) else ''
    res['第三四分位数'] = data.third_quartile if (hasattr(data, 'third_quartile')) else ''
    res['中央値'] = data.median if (hasattr(data, 'median')) else ''
    res['第一四分位数'] = data.first_quartile if (hasattr(data, 'first_quartile')) else ''
    res['特殊'] = data.special if (hasattr(data, 'special')) else ''
    return res


if __name__ == '__main__':
    os.makedirs('csv', exist_ok=True)
    args = sys.argv
    f = open('csv/' + args[1] + '.csv', 'w')
    data_list = create_dict_list(args[1], int(args[2]))
    writer = csv.DictWriter(f, data_list[0].keys())
    writer.writeheader()
    for row in data_list:
        writer.writerow(row)
    f.close()
