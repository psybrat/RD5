# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        utils
# Purpose:
#
# Author:      psybrat
#
# Created:     14.12.2020
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

    if line[0] == '0':
        return [el for el in map(float, line[1:])]
    else:
        return [el for el in map(float, line[1:-1])]


def csv_parser(csv_path):
    """
    param:
        csv_path: string
            Путь к .csv файлу

    Парсим .csv файл с параметрами расчёта и возвращаем dict с ключом conditions
    для параметров условия и elements со списком элементов.

    >>> path = 'test_csv_parser.csv'
    >>> res = csv_parser(path)
    >>> res == {'conditions': [40.0, 0.01, 1.125, 1.152, 1.0, 2.0], 'elements': [[5.0, 70.0, 0.013, 7.6e-05, 6.0], [10.0, 70.0, 0.013, 7.6e-05, 6.0], [15.0, 50.0, 0.015, 1e-05, 0.0]]}
    True
    """
    #TODO Обработка запятых
    #TODO перевести list в dict
    res = {'conditions': [], 'elements': []}
    with open(csv_path, "r") as f_obj:
        reader = csv.reader(f_obj, delimiter=';')
        for line in reader:
            if line[0] == '0':
                res['conditions'] = line_clear(line)
            if line[0].isdigit() and int(line[0]) > 0:
                res['elements'].append(line_clear(line))
    return res


def get_real(message, name="real",default=None):
    """
    param:
        message: string
            Выводимое пользователю сообщение
        name: string
            Сервисное имя, я не помню, зачем
        default: float
            Число по умолчанию, в случае пустого ответа пользователя

    Запрашивает сообщением message у пользователя число и возвращает его в типе float
    """
    class RangeError(Exception): pass
    message += ": " if default is None else " [{0}]: ".format(default)
    while True:
        try:
            line = input(message)
            if not line and default is not None:
                return default
            i = float(line)
            if i >= 0:
                return i
            else:
                raise RangeError("{0} may not be 0".format(name))
            return i
        except RangeError as err:
            print("ERROR", err)
        except ValueError as err:
            print("ERROR {0} must be an real".format(name))


if __name__ == '__main__':
    csv_parser('input_data')
    import doctest
    doctest.testmod()
