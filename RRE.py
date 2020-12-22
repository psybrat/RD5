# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        RRE
# Purpose:
#
# Author:      psybrat
#
# Created:     27.06.2020
#-------------------------------------------------------------------------------
import math
import utils

from radiators import FinnedRadiator
from elements import ElectronicElement, SetElectronicElements

from radiators import fin_radiator_generator as radiator_generator



def f1xy(L, B, n, alff, dks):
    """
    param:
        L : float
            Длина ребра радиатора [м]
        B : float
            Ширина радиатора [м]
        alff : float
            Эффективный коэффициент теплоотдачи для 1 м2 основания радиатора [Вт/м2*К]
        dks : float
            Ещё один неизвестный коэффициент.

    Понятия не имею, что делает эта функция. Вроде как, считает растекание
    теплоты по радиатору в направлениях l и b.
    """
    def f1(L, B, alf3, dks):
        by = 1.2 * alf3 * L**2
        r = 2 * math.sqrt(by)
        px = B/L * math.sqrt(by * (1.5 - 1/(1 + math.sinh(r)/r)))
        dkss = dks/B
        kx = 2 * math.sinh(px * dkss) * math.cosh(0.5 * px)/math.sinh(px)
        fi = kx * math.cosh(0.5 * px) - math.cosh(px * dkss) + 1
        return fi

    f1x = f1(L/n, B, alff, dks)
    f1y = f1(B, L/n, alff, dks)
    return f1x*f1y


def number_Gr(t, dt_max, l):
    """
    param:
        t: float
            Температура среды [*C]
        dt_max: float
            Максимально допустимая разница температур среда-элемент [*C]
        l: float
            Определяющий размер [м]

    Возвращает число Грасгоффа
    """
    # Дописать расчёт числа 303959E5
    gr = 303959E5 * dt_max * l ** 3/(273 + t)
    return gr


def nusselt_free_plane(t_air, dt_max, l):
    """
    param:
        t_air: float
            Температура среды [*C]
        dt_max: float
            Максимально допустимая разница температур среда-элемент [*C]
        l: float
            Высота стенки (определяющий размер) [м]

    Возвращает число Нуссельта для свободной конвекции на плоской вертикальной стенке
    """
    # a = Gr*Pr, Pr = 0.7
    a = 0.7 * number_Gr(t_air, dt_max, l)

    if a <= 5E2:
        nu = 1.18 * a ** 0.125
    else:
        nu = 0.135 * a ** 0.33
    return nu


def nusselt_free_fins(t_air, dt_max, dell, l):
    """
    param:
        t_air : float
            Температура окружающей среды
        dt_max : float
            Максимальная разница температур [*C]

    Число Нуссельта для межрёберного пространства. tb - температура воздуха,
    dt_max - максимально допустимая разница температур (среда-элемент),
    t_air - температура среды
    """
    # Грасгофф. определяющий размер - половина расстояния между рёбер. Т = 50
    c = number_Gr(t_air, dt_max, dell) * dell/l
    q = 12.84 + c
    # число нуссельта
    nu = 6 * c/q * 1/(1 + math.sqrt(1 + (51.4 * c)/q ** 2))
    return nu


def number_Alfa(nu, l, t = 50):
    """
    param:
        nu: float
            Число Нуссельта
        l: float
            Определяющий размер [м]
        t: float
            Температура потока [*C]

    Возвращает коэффициент теплоотдачи для воздуха [Вт/м^2*К]. Теплопроводность взята при Т=50
    """
    # Дописать расчёт теплопроводности воздуха
    alfa = 0.0283 * nu/l
    return alfa


def number_Alfa_radiation(t_air, dt_max, dell, h1):
    """
    param:
        tb: float
            Температура среды [*C]
        dt_max: float
            Максимально допустимая разница температур среда-элемент [*C]
        dell: float
            Половина расстояния между рёбер [м]
        h1: float
            Высота рёбер [м]

    Возвращает коэффициент теплоотдачи лучистый для плоской alfl
    и оребрённой alflr стороны [Вт/м^2*К]
    """
    # Температура поверхности радиатора
    tr = t_air + dt_max
    # Безразмерный параметр хз чего. Половина расстояния между рёбрами, делёная на сумму высоты и половину расстояния.
    fi1 = dell/(h1 + dell)
    # Теплообмен излучением с воздухом через постоянную Больцмана. Зачем делим на Дтр?
    alfl = 4.5E-8 * ((tr + 273)**4 - (t_air + 273)**4)/dt_max
    # Получаем альфу лучистую
    alflr = alfl * fi1
    return alfl, alflr


def alpha2power(alpha, surface, diff_t):
    """
    param:
        alpha : float
            коэффициент теплоотдачи [Вт/м*К]
        surface : float
            площадь контактной поверхности [м^2]
        diff_t : float
            Разность температур поверхности и окружающей среды [*C]

    Возвращает мощность P [Вт], излучаемую с площади surface при разности температур diff_t
    и коэффициенте теплоотдачи alpha.
        P = alpha * surface * diff_t
    """
    return alpha*surface*diff_t


def cooling_power(radiator, tb, dtr, n, fr1, k, dks, s):
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
        s: float
            Шаг рёбер

    Расчёт мощности [Вт] отводимой радиатором в данных условиях
    """
    l = radiator.length
    b = radiator.width
    h1 = radiator.fin_height


    dell = radiator.half_step()

    fr = radiator.fins_surface_with_element(fr1)
    f0 = radiator.full_surface()
    fp = radiator.flat_surface()


    nu_fins = nusselt_free_fins(tb,dtr, dell, l)
    nu_plane = nusselt_free_plane(tb, dtr, l)

    pr = alpha2power(number_Alfa(nu_fins, dell), fr, dtr)    # Мощность, отводимая боковй поверхностью рёбер
    p0 = alpha2power(number_Alfa(nu_plane, l), f0, dtr)     # Мощность, отводимая остальной поверхностью

# ----- Начинается расчёт лучевого теплообмена --------------------
    alfl, alflr = number_Alfa_radiation(tb, dtr, dell, h1)


    pl0 = alpha2power(alfl, f0, dtr)        # Излучение с поверхностей радиатора, но не между рёбер
    plr = alpha2power(alflr, fr, dtr)       # Излучение с поверхностей рёбер

    p2 = pr + p0 + pl0 + plr                    # Суммарная теплоотдача, конвекция рёбра + лучи рёбра + конвекция остальное + лучистое остальное

    if k == 1:
        pp = alpha2power(number_Alfa(nu_plane, l), fp, dtr)   # Мощность (конвективная), отводимая от неоребрённой поверхности
        plp = alpha2power(alfl, fp, dtr)                        # Мощность (лучистая), отводимая с плоской стороны радиатора
        p1 = pp + plp
    else:
        p1 = p2                                 # Здесь считаем, что на второй стороне такие же рёбра, как и на первой.

    alff = (p1 + p2)/(l*b*dtr)                  # Это подсчёт альфы эффективной. Полная мощность с основания.

    bet = fp/(4*n*dks**2) * f1xy(l, b, n, alff, dks)       # Вытекающий коэффициент растекания тепла
    pp = alpha2power(alff, fp, dtr)/bet

    print("pp = {0}; fr = {1}".format(pp, fr))
    return pp


def main():
    gather_elements = SetElectronicElements()

    filename = 'input_data'
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

    conditions = {'tb': tb, 'dtr': dtr, 'n':n, 'fr1': fr1, 'k': k, 'dks': dks, 's': s}

    for el in radiator_generator(k, length=lm, max_width=bm):
        l, b = el
        radiator = FinnedRadiator(l, b, h1)
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
