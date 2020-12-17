# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        модуль1
# Purpose:
#
# Author:      g.ukryukov
#
# Created:     27.06.2018
# Copyright:   (c) g.ukryukov 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import math
import utils


class EdgeRadiator():
    """
    Ребристый радиатор.
    param ::
        length : int
            Длина радиатора вдоль ребра (длина ребра) [м]
        width : int
            Ширина радиатора [м]
        fin_heigth : int
            Высота рёбер [м]
        base_thick : int
            Толщина основания [м]
        fin_thick : int
            Толщина рёбер [м]
        step : int
            Шаг рёбер [м]


    >>> rad = EdgeRadiator(30E-3, 35E-3, 10E-3)
    >>> rad.edge_number()
    3.0
    >>> round(rad.flat_surface(), 7)
    0.00105
    >>> round(rad.half_step(), 7)
    0.0045
    >>> round(rad.fins_surface(), 7)
    0.0014

    """
    def __init__(self, width, length, fin_height, step=10E-3, base_thick=4E-3, fin_thick=1E-3):
        self.length = length
        self.width = width
        self.fin_height = fin_height
        self.base_thick = base_thick
        self.fin_thick = fin_thick
        self.step = step


    def __repr__(self):
        res = \
        """
<Radiator>
        length {}
        width {}
        fin_heigth {}
        base_thick {}
        fin_thick {}
        step {}
        """.format(self.length, self.width, self.fin_height, self.base_thick, self.fin_thick, self.step)
        return res

    def edge_number(self):
        """
        nz
        Количество рёбер. []
        """
        return (self.width - self.fin_thick) // self.step + 1

    def flat_surface(self):
        """
        fp
        Площадь основания радиатора. [м^2]
        """
        res = self.width * self.length
        return res

    def half_step(self):
        """
        dell
        Половина расстояния между рёбер. Используется в качестве определяющего
        размера в критериях подобия. [м]
        """
        res = (self.step - self.fin_thick) / 2
        return res

    def fins_surface(self):
        """
        fr
        Площадь поверхности всех рёбер. [м^2]
        """
        res = (self.edge_number() - 1)  * (self.length * self.fin_height * 2)
        return res


    def fins_surface_with_element(self, fr1):
        """
        Площадь поверхности всех рёбер после вычета площади поверхности рёбер,
        срезанных элементом.
        params::
            fr1 : int
                Площадь поверхности срезанных рёбер [м^2]
        """
        res = self.fins_surface() - fr1
        if res > 0:
            return res
        else:
            return 0


    def full_surface(self):
        """
        f0
        Полная площадь поверхности радиатора без боковых поверхностей рёбер. [м^2]
        """
        res = self.length * self.width + 2 * self.fin_height * self.length +  \
            2 * self.base_thick * (self.length + self.width) + \
            2 * self.edge_number() * self.fin_height * self.fin_thick
        return res


class ElectronicElement():
    """
    Электрический элемент.
    param::
        power : float
            Тепловая мощность элемента [Вт]
        max_t : float
            Максимально допустимая температура элемента [*C]
        contact_space : float
            Площадь поверхности контакта с радиатором охлаждения [м^2]
        temp_resist : float
            Контактное тепловое сопротивление Элемент-Радиатор (Обычно это КПТ-8) [м^2*К/Вт]
        viborka : int
            Признак выборки под элемент (1..6)

    >>> params = [5, 70, 0.013, 7.6e-05, 6]
    >>> el = ElectronicElement(*params)
    >>> round(el.permissible_overheating(40), 2) == 29.97
    True
    >>> round(el.fr1_exclude_surface(0.01), 7) == 0.0028
    True
    """

    SV = [1E-2, 3E-2, 5E-2, 7.2E-2, 1.05E-1, 1.4E-1]

    def __init__(self, power, max_t, contact_space, temp_resist, viborka):
        self.power = power
        self.max_t = max_t
        self.contact_space = contact_space
        self.temp_resist = temp_resist
        self.viborka = viborka


    def __repr__(self):
        return \
        """
        <ElectronicElement>
        power: {}
        max_t: {}
        contact_space: {}
        temp_resist: {}
        viborka: {}
        """.format(self.power, self.max_t, self.contact_space, self.temp_resist, self.viborka)


    def permissible_overheating(self, air_temp):
        """
        param ::
            air_temp : float
                Температура окружающей среды (среды охлаждения)

        Возвращает допустимый перегрев элемента относительно окружающей среды [*C]
        dTдоп = Tmax - t.air * P * sigmaT / S.контакта
        """
        return self.max_t - air_temp - self.power * self.temp_resist / self.contact_space


    def fr1_exclude_surface(self, fin_height):
        """
        param ::
            fin_height : float
                Высота ребра используемого радиатора [м]

        Возвращает площадь боковой поверхности рёбер радиатора, изымаемая при установке
        элемента на ребристую сторону радиатора. Рассчитывается исходя из
        признака выборки по РД5.8794-88 (или ОСТ) [м^2]
        """
        return 2 * self.SV[self.viborka - 1] * fin_height


class SetElectronicElements():
    """
    Набор элементов на одном радиаторе.

    params ::
        elements : list of <ElectronicElement>

    >>> params = [5, 70, 0.013, 7.6e-05, 6]
    >>> el1 = ElectronicElement(*params)
    >>> params = [7, 50, 0.01, 7.6e-05, 1]
    >>> el2 = ElectronicElement(*params)
    >>> pull = SetElectronicElements(el1, el2)
    >>> print(pull)
    <SetElectronicElements:len=2; powers:[5, 7]>
    >>> params = [10, 65, 0.05, 7.6e-05, 5]
    >>> el3 = ElectronicElement(*params)
    >>> pull.add(el3)
    >>> print(pull)
    <SetElectronicElements:len=3; powers:[5, 7, 10]>
    >>> print(pull.dtr_permissible_overheating(40))
    9.9468
    """
    def __init__(self, *elements):
        self.pull = []
        self.pull.extend(elements)


    def __repr__(self):
        return "<SetElectronicElements:len={}; powers:{}>".format(len(self.pull), \
                                                            [el.power for el in self.pull])


    def add(self, element):
        """
        Добавляет элемент <ElectronicElement> в набор элементов.

        params ::
            element : <ElectronicElement>
                Объект класса <ElectronicElement>
        """
        self.pull.append(element)


    def dtr_permissible_overheating(self, air_temp):
        """
        Возвращает минимальное значение допустимого перегрева для набора элементов
        на радиаторе.

        params ::
            air_temp : float
                Температура охлаждающей среды
        """
        return min([el.permissible_overheating(air_temp) for el in self.pull])


    def full_power(self):
        """
        Возвращает суммарную тепловую мощность добавленных элементов
        """
        return sum([el.power for el in self.pull])


    def fr1_full_exclude_surface(self, fin_height):
        """
        Возвращает суммарную площадь боковых поверхностей, изъятых при установке
        элементов на ребристую сторону радиатора.
        """
        return sum([el.fr1_exclude_surface(fin_height) for el in self.pull])


def f1(l, b, alf3, dks):
    by = 1.2 * alf3 * l**2
    r = 2 * math.sqrt(by)
    px = b/l * math.sqrt(by * (1.5 - 1/(1 + math.sinh(r)/r)))
    dkss = dks/b
    kx = 2 * math.sinh(px * dkss) * math.cosh(0.5 * px)/math.sinh(px)
    fi = kx * math.cosh(0.5 * px) - math.cosh(px * dkss) + 1
    return fi

def get_real(message, name="real",default=None):
    """
    Запрашивает у пользователя ввод параметра i, оповещая сообщением message
    Использует по умолчанию значение default. Возвращает Real.
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


def number_Gr(t, dt_max, l):
    """
    Число Грасгоффа. Температура среды t °C, максимально допустимая
    разница температур (среда-элемент) dt_max, определяющий размер l

    """
    # Дописать расчёт числа 303959E5
    gr = 303959E5 * dt_max * l ** 3/(273 + t)
    return gr


def number_Nu_plane(t_air, dt_max, l):
    """
    Число Нуссельта для плоской вертикальной стенки, l - высота стенки
    dt_max - максимально допустимая разница температур (среда-элемент),
    t_air - температура среды
    """
    # a = Gr*Pr, Pr = 0.7
    a = 0.7 * number_Gr(t_air, dt_max, l)

    if a <= 5E2:
        nu = 1.18 * a ** 0.125
    else:
        nu = 0.135 * a ** 0.33
    return nu


def number_Nu_edge(t_air, dt_max, dell, l):
    """
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
    nu - число Нуссельта, l - определяющий размер
    Коэффициент теплоотдачи для воздуха. Теплопроводность взята при Т=50
    """
    # Дописать расчёт теплопроводности воздуха
    alfa = 0.0283 * nu/l
    return alfa


def number_Alfa_radiation(t_air, dt_max, dell, h1):
    """
    Коэффициент лучистой теплоотдачи.
    tb - температура среды,
    dt_max (dtr) максимально допустимая разница температур (среда-элемент)
    dell - половина расстояния между рёбер
    h1 - высота ребра
    На выходе: alfl - с плоской стороны, alflr - с ребристой
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


def full_p():
    # количество рёбер
    nz = (b - br)/s + 1
    # полная площадь поверхности основания
    fp = l * b
    # половина расстояния между рёбрами
    dell = (s - br)/2
    if k == 1:
# -------- теплоотдача от неоребрённой поверхности радиатора -----------
        pp = p_plane(tb, dtr, l, b)
# -------закончен расчёт теплоотдачи от неоребрённой поверхности -------

def main():
    L1 = [3.6E-2, 3.6E-2, 5E-2, 5E-2, 5E-2, 8E-2, 8E-2, 8E-2, 1E-1, 1E-1,  1E-1,
            1.25E-1, 1.25E-1, 1.25E-1]
    B1 = [3.2E-2, 7.2E-2, 3.2E-2, 5.2E-2, 9.2E-2, 3.2E-2, 7.2E-2, 1.22E-1,
            5.2E-2, 9.2E-2, 1.52E-1, 7.2E-2, 1.22E-1, 1.52E-1]
    L2 = [5E-2, 5E-2, 8E-2, 8E-2, 1E-1, 1E-1, 1E-1, 1.25E-1, 1.25E-1,  1.25E-1]
    B2 = [5.2E-2, 9.2E-2, 7.2E-2, 1.22E-1, 5.2E-2, 9.2E-2, 1.52E-1, 7.2E-2,
            1.22E-1, 1.52E-1]
    SV = [1E-2, 3E-2, 5E-2, 7.2E-2, 1.05E-1, 1.4E-1]   # это должны быть длины изымаемых рёбер

    tb = get_real("Введите температуру воздуха, °C", default = 40)
    h1 = get_real("введите высоту ребра, м", default = 0.01)
    lm = get_real("максимально допустимая высота радиатора, м", default = 1.125)
    bm = get_real("максимально допустимая ширина радиатора, м", default = 1.152)
    k = get_real("Односторонний или двусторонний радиатор (1/2) ", default = 1)
    n = int(get_real("Количество ППП, установленных на радиаторе", default = 1))
    k1 = get_real("Имеется ли выборка (0/1)", default = 1)

    pi = list()
    k2 = list(); kkr = list(); tdop = list(); s0 = list()

    gather_elements = SetElectronicElements()
    for i in range(n):
        temp2 = []
        temp = get_real("Мощность элемента {0}, Вт".format(i), default = 5)
        pi.append(temp)
        temp2.append(temp)
        temp = get_real("Максимально допустимая температура элемента {0}, °С".format(i), default = 70)
        tdop.append(temp)
        temp2.append(temp)
        temp = get_real("Площадь контакта элемента {0}, м2".format(i), default = 0.013)
        s0.append(temp)
        temp2.append(temp)
        temp = get_real("Удельное контактное тепловое сопротивление элемента {0} м2*К/Вт".format(i), default = 0.76E-4)
        kkr.append(temp)
        temp2.append(temp)
        temp = get_real("Признак выборки под ППП {0} (1..6)".format(i), default = 6)
        k2.append(temp)
        temp2.append(temp)
        element = ElectronicElement(*temp2)
        gather_elements.add(element)

##    filename = 'input_data.csv'
##    data = utils.csv_parser(filename)
##    tb, h1, lm, bm, k, n = data['conditions']
##    for el in data['elements']:
##        element = ElectronicElement(*el)
##        gather_elements.add(element)


##    s = 0.01
##    br = 0.001
##    h0 = 0.005
    dks = math.sqrt(s0[0]/3.14)  #почему? Иди нахуй. вот почему.
##    p = 0
##    dtr = 1000    # допустимый перегрев
##    fr1 = 0

##    for i in range(n):
##        kk = k2[i]              # здесь хранится номер выборки i-того элемента
##        p += pi[i]            # здесь собираем суммарную мощность ППП
##        fr1 += 2 * SV[kk-1] * h1 * k1     # боковая поверхность рёбер, изымаемая при выборке
##        tdop[i] -= tb + pi[i] * kkr[i] / s0[i]  # расчёт допустимого перегрева (минимального)
##        if tdop[i] <= dtr:                      #  --//--
##            dtr = tdop[i]                       #  --//--
##    print(dtr)
##    print(gather_elements.dtr_permissible_overheating(tb))
    fr1 = gather_elements.fr1_full_exclude_surface(h1)
    dtr = gather_elements.dtr_permissible_overheating(tb)
    p = gather_elements.full_power()

    for i in range(len(L1)):
        print('New from len L1')
# Здесь подбирается радиатор из сетки размеров для одной и двх сторон
        if k == 1:
            l = L1[i]
            b = B1[i]
        else:
            l = L2[i]
            b = B2[i]
# ------------------------------------------------------------------
# Если радиатор из списка больше допустимого размера, значит подборки нет
        if (l > lm) or (b > bm):
            print("Финита ля комедия. Радиаторов не существует. Это фантастика")
            break
# ------------------------------------------------------------------

        radiator = EdgeRadiator(b, l, h1)

        dell = radiator.half_step()
        fr = radiator.fins_surface_with_element(fr1)
        f0 = radiator.full_surface()
        fp = radiator.flat_surface()


        nu_edge = number_Nu_edge(tb,dtr, dell, l)
        nu_plane = number_Nu_plane(tb, dtr, l)

        pr = number_Alfa(nu_edge, dell) * fr * dtr    # Мощность, отводимая боковй поверхностью рёбер
        p0 = number_Alfa(nu_plane, l) * f0 * dtr   # Мощность, отводимая остальной поверхностью

# ----- Начинается расчёт лучевого теплообмена --------------------
        alfl, alflr = number_Alfa_radiation(tb, dtr, dell, h1)

        pl0 = alfl*f0*dtr                           # Излучение с поверхностей радиатора, но не между рёбер
        plr = alflr*fr*dtr                          # Излучение с поверхностей рёбер

        p2 = pr + p0 + pl0 + plr                    # Суммарная теплоотдача, конвекция рёбра + лучи рёбра + конвекция остальное + лучистое остальное

        if k == 1:
            pp = number_Alfa(nu_plane, l) * fp * dtr   # Мощность (конвективная), отводимая от неоребрённой поверхности
            plp = alfl * fp * dtr                   # Мощность (лучистая), отводимая с плоской стороны радиатора
            p1 = pp + plp
        else:
            p1 = p2                                 # Здесь считаем, что на второй стороне такие же рёбра, как и на первой.

        alff = (p1 + p2)/(l*b*dtr)                  # Это подсчёт альфы эффективной. Полная мощность с основания.
        f1x = f1(l/n, b, alff, dks)                 # Это за гранью моего понимания. Возможно, растекание тепла по основанию.
        f1y = f1(b, l/n, alff, dks)
        bet = fp/(4*n*dks**2) * f1x * f1y           # Вытекающий коэффициент растекания тепла
        pp = fp * alff * dtr/bet
        print("pp = {0}; fr = {1}".format(pp, fr))
        if pp >= p:
            print("Параметры радиатора: длина {0}, ширина {1}, выота ребра {2}, площадь {3}".format(l,b,h1, l*b))
            break

if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
