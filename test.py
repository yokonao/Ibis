import main
import os
import csv

if __name__ == '__main__':
    f = open('test.csv', 'w')
    data_list = main.create_dict_list('example', 24)
    writer = csv.DictWriter(f, data_list[0].keys())
    writer.writeheader()
    for row in data_list:
        writer.writerow(row)
    f.close()
    f = open('csv/example.csv', 'r')
    expected = f.readlines()
    print(expected)
    f.close()
    f = open('test.csv', 'r')
    actual = f.readlines()
    print(actual)
    f.close()
    os.remove('test.csv')
    assert(expected == actual)
