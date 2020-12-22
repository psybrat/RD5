# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        RRP
# Purpose:
#
# Author:      psybrat
#
# Created:     10.07.2020

#-------------------------------------------------------------------------------
import math
import utils

from RRE import f1xy, alpha2power
from radiators import FinnedRadiator
from elements import ElectronicElement, SetElectronicElements
from radiators import fin_radiator_generator as radiator_generator
from utils import get_real


def reynolds(w, d):
    """
    param:
        w: float
            Скорость потока [м/с]
        d: float
            Определяющий размер [м]

    Возвращает число рейнольдса для воздуха.
    """
    return 55710.3 * w * d


def nusselt_force_fins(re, q):
    """
    param:
        re: float
            Число рейнольдса для межрёберного пространства
        q: float
            Отношение длины канала к гидравлическому диаметру канала

    Возвращает число Нуссельта для принудительной конвекции в межрёберном канале
    """

    def nki(t):
        """
        param:
            t: float
                Температура [*C]

        Пока без понятия, что это за функция.
        Какой-то поправочный коэффициент.
        """
        T = [1, 2, 5, 10, 15, 20, 30, 40, 50]
        B3 = [1.9, 1.7, 1.44, 1.28, 1.18, 1.13, 1.05, 1.02, 1]
        for i in range(len(T)):
            if(t >= T[i])and(t <= T[i+1]):
                return B3[i] - (B3[i] - B3[i+1]) * (t - T[i]) / (T[i+1] - T[i])

    if re <= 2200:
        a = 0.7*re/q
        if a <= 5:
            nu = 9
        elif a <= 100:
            nu = 8.4*a**0.045
        else:
            nu = 2.32*a**0.33
    else:
        fl = nki(q)    # ????
        if (q <= 50):
            nu = fl*0.0216*re**0.8
        else:
            nu = 0.0216*re**0.8
    return nu


def nusselt_force_plane(re):
    """
    param:
        re: Float
            Число рейнольдса для плоской поверхности

    Возвращает число Нуссельта для принудительной конвекции на плоскости.
        """
    if re >= 1E5:
        nu = 0.084*re**0.8
    else:
        nu = 0.792*re**0.5
    return nu


def number_Alfa_radiation(t_air, dt_max, dell, h1):
    """
    param:
        t_air: float
            Температура окружающей среды [*C]
        dt_max: float
            Максимально допустимая разница температур (среда-элемент) [*C]
        dell: float
            Половина расстояния между рёбер [м]
        h1: float
            Высота рёбер [м]

    Возвращает коэффициенты теплоотдачи лучистой для плоской (alfl)
    и оребрённой (alflr) стороны. [Вт/м^2*К]
    """
    tr = t_air + dt_max         # Температура поверхности радиатора
    fi1 = dell/(h1 + dell)      # Безразмерный параметр хз чего. Половина расстояния между рёбрами, делёная на сумму высоты и половину расстояния.
    alfl = 4.5E-8 * ((tr + 273)**4 - (t_air + 273)**4)/dt_max    # Теплообмен излучением с воздухом через постоянную Больцмана. Зачем делим на Дтр?
    alflr = alfl * fi1                    # Получаем альфу лучистую
    return alfl, alflr


def number_Alfa(nu, l, t=50):
    """
    param:
        nu: float
            Число Нуссельта
        l: float
            Определяющий размер [м]
        t: float
            Температура потока [*C]

    Возвращает коэффициент теплоотдачи для воздуха [Вт/м^2*К]. Теплопроводность взята при Т=50 *С
    """
    #TODO Дописать расчёт теплопроводности воздуха
    alfa = 0.0283 * nu/l
    return alfa



def cooling_power(radiator, tb, dtr, n, fr1, k, dks, w, p):
    """
    param:
        radiator : FinnedRadiator()
            Экземпляр класса радиатора.
        tb : float
            Температура окружающей среды [*C]
        dtr : float
            Максимально допустимая разница температур [*C]
        n : integer
            Количество установленных элементов
        fr1 : float
            Площадь изымаемых боковых поверхностей [м^2]
        k : integer
            Одно- или двусторонний радиатор
        dks : float
            Магическая переменная
        w : float
            Скорость потока среды [м/с]
        p : float
            Суммарная тепловая мощность элементов [Вт]

    Расчёт мощности [Вт] отводимой радиатором в данных условиях
    """

    pr = p*0.7
    l = radiator.length
    h1 = radiator.fin_height
    b = radiator.width
    dell = radiator.half_step()
    fr = radiator.fins_surface_with_element(fr1)
    assert fr > 0
    f0 = radiator.full_surface()
    fp = radiator.flat_surface()
    br = radiator.fin_thick
    s = radiator.step
    dk = radiator.equal_diameter()        # Гидравлический диаметр
    q = l/dk                    # Отношение длины канала к калибру

    wr = w * s / (s - br)           # ???

    dtoop = dtr

    rer = reynolds(wr, dk)
    nur = nusselt_force_fins(rer, q)

    dtb = (0.9E-3 * pr)/(w * (2 * dell * h1))    # ????
    dtrr = pr / (number_Alfa(nur, dk) * fr)         #  перегрев при текущей альфа и площади  (может внезапно стать бесконечностью)
    mh1 = 0.15 * math.sqrt(number_Alfa(nur, dk) / br) * h1     # очень похоже на коэффициент эффективности, но не понятно, откуда 0.15
    z = math.tanh(mh1)/mh1              # ----//-----
    dtr = dtrr/z + dtb/2                #???? О_о

    re = reynolds(w, l)
    nu_plane = nusselt_force_plane(re)
    p0 = alpha2power(number_Alfa(nu_plane, l), f0, dtr)

    alfl, alflr = number_Alfa_radiation(tb, dtr, dell, h1) # Излучение
    plr = alpha2power(alflr, fr, dtr)   # Альфа с поправкой для рёбер
    pl0 = alpha2power(alfl, f0, dtr)    # Плоская часть с боков. Альфа как для плоской

    p2 = pr + p0 + pl0 + plr               # Сумма мощностей. Рёбра конвекция + Рёбра лучистая + поверхность конвекция + поверхность лучистая

    if k == 1:                       # Если односторонинй радик, то мощность как плоская
        pp = alpha2power(number_Alfa(nu_plane, l), fp, dtr)
        plp = alpha2power(alfl, fp, dtr) # Альфа для плоской части
        p1 = pp + plp
    else:                               # Если двусторонний, то копируем.
        p1 = p2

    alff = (p1 + p2)/(fp*dtr)           # Суммарная альфа

    bet = fp/(4*n*dks**2) * f1xy(l, b, n, alff, dks)      # Какой-то коэффициент растекания
    pp = alpha2power(alff, fp, dtoop) / bet
    print("PP : {0}; alff : {1}, w : {2}, wr : {3}".format(pp, alff, w, wr))
    return pp


def main():

    w = get_real("Скорость потока среды, м/с", default = 1)       # Единственный новый параметр

    gather_elements = SetElectronicElements()

    filename = 'test_RRP_input_data.csv'
    data = utils.csv_parser(filename)
    tb, h1, lm, bm, k, s = data['conditions']

    for el in data['elements']:
        element = ElectronicElement(*el)
        gather_elements.add(element)

    s0 = 0.2e-3 #изначально бралась площадь контакта первого элемента (хз почему)
    dks = math.sqrt(s0/3.14)  #почему? Иди нахуй. вот почему.

    fr1 = gather_elements.fr1_full_exclude_surface(h1, step=s)
    dtr = gather_elements.dtr_permissible_overheating(tb)
    p = gather_elements.full_power()
    n = len(gather_elements)

    conditions = {'tb': tb, 'dtr': dtr, 'n': n, 'fr1': fr1, 'k': k, 'dks': dks, 'w': w, 'p': p}

    for el in radiator_generator(k, length=lm, max_width=bm):
        l, b = el
        radiator = FinnedRadiator(l, b, h1, step=s)
        pp = cooling_power(radiator, **conditions)

        if pp >= p:
            print("Параметры радиатора: длина {0}, ширина {1}, выота ребра {2}, площадь {3}".format(l,b,h1, l*b))
            break

    if pp < p:
        print('Невозможно подобрать радиатор в заданных геометрических рамках')


if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
