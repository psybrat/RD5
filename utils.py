# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        модуль1
# Purpose:
#
# Author:      g.ukryukov
#
# Created:     14.12.2020
# Copyright:   (c) g.ukryukov 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import csv


def line_clear(line):
    """
    param:
        line: list
            Список параметров из input файла

    Преобразуем список параметров:
        1. Удаляем первый элемент для элементов 'conditions' (line[0] == '0')
        Удаляем первый и последний элемент 'elements' (line[0] > 0 порядковый номер элемента)
        2. Транслируем все значения в float.

    >>> print(line_clear(['0', '40', '0.01', '1.125', '1.152', '1', '2']))
    [40.0, 0.01, 1.125, 1.152, 1.0, 2.0]
    >>> print(line_clear(['1', '5', '70', '0.013', '0.000076', '6', '']))
    [5.0, 70.0, 0.013, 7.6e-05, 6.0]
    """
#    print(line)
    if line[0] == '0':
        return [el for el in map(float, line[1:])]
    else:
        return [el for el in map(float, line[1:-1])]


def csv_parser(csv_path):
    res = {'conditions': [], 'elements': []}
    with open(csv_path, "r") as f_obj:
        reader = csv.reader(f_obj, delimiter=';')
        for line in reader:
            if line[0] == '0':
                res['conditions'] = line_clear(line)
            if line[0].isdigit() and int(line[0]) > 0:
                res['elements'].append(line_clear(line))
    return(res)


if __name__ == '__main__':
    csv_parser('input_data.csv')
    import doctest
    doctest.testmod()
