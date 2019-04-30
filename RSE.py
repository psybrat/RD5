# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        модуль1
# Purpose:
#
# Author:      G.Ukryukov
#
# Created:     05.03.2019
# Copyright:   (c) G.Ukryukov 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

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
    a = 0.7 * number_Gr(t_air, dt_max, l)    # a = Gr*Pr

    if a <= 5E2:
        nu = 1.18 * a ** 0.125
    elif a <= 2E7:
        nu = 0.54 * a ** 0.25
    else:
        nu = 0.135 * a ** 0.33
    return nu

def number_Alfa(nu, l, t = 50):
    """
    nu - число Нуссельта, l - определяющий размер
    Коэффициент теплоотдачи для воздуха. Теплопроводность взята при Т=50
    """
    # Дописать расчёт теплопроводности воздуха
    alfa = 0.0283 * nu/l
    return alfa

def main():
    L1 = [0.036, 0.036, 0.05, 0.05, 0.05, 0.08, 0.08, 0.08, 0.1, 0.1, 0.1,
            0.125, 0.125, 0.125]
    L2 = [0.05, 0.05, 0.05, 0.08, 0.08, 0.08, 0.1, 0.1, 0.1, 0.125, 0.125,
            0.125, 0.125, 0.125]
    B1 = [0.032, 0.072, 0.032, 0.052, 0.092, 0.032, 0.072, 0.122, 0.052, 0.092,
            0.152, 0.072, 0.122, 0.152]
    B2 = [0.032, 0.052, 0.092, 0.032, 0.072, 0.122, 0.152, 0.092, 0.152, 0.072,
            0.122, 0.152, 0.152, 0.152]
    SV = [4, 8, 15, 23, 34, 50]

    tb = get_real("Введите температуру воздуха, °C", default = 40)
    h1 = get_real("введите высоту ребра, м", default = 0.0125)
    lm = get_real("максимально допустимая высота радиатора, м", default = 1.125)
    bm = get_real("максимально допустимая ширина радиатора, м", default = 1.152)
    k = get_real("Односторонний или двусторонний радиатор (1/2) ", default = 1)
    n = int(get_real("Количество ППП, установленных на радиаторе", default = 1))
    k1 = get_real("Имеется ли выборка (0/1)", default = 0)

    pi = list()
    k2 = list(); kkr = list(); tdop = list(); s0 = list()
    for i in range(n):
        temp = get_real("Мощность элемента {0}, Вт".format(i), default = 15)
        pi.append(temp)
        temp = get_real("Максимально допустимая температура элемента {0}, °С".format(i), default = 70)
        tdop.append(temp)
        temp = get_real("Площадь контакта элемента {0}, м2".format(i), default = 0.013)
        s0.append(temp)
        temp = get_real("Удельное контактное тепловое сопротивление элемента {0} м2*К/Вт".format(i), default = 0.76E-4)
        kkr.append(temp)
        temp = get_real("Признак выборки под ППП {0} (1..6)".format(i), default = 5)
        k2.append(temp)

    s = 0.007
    d = 0.003
    dks = math.sqrt(s0[0]/3.14)  #почему? Иди нахуй. вот почему.
    p = 0
    dtr = 1000    # допустимый перегрев
    fs1 = 0

    for i in range(n):
        kk = k2[i]              # здесь хранится номер выборки i-того элемента
        p += pi[i]            # здесь собираем суммарную мощность ППП
        fs1 += 3.14 * d * SV[kk] * h1 * k1     # боковая поверхность штырей, изымаемая при выборке
        tdop[i] -= tb - pi[i] * kkr[i] / s0[i]  # расчёт допустимого перегрева (минимального)
        if tdop[i] <= dtr:                      #  --//--
            dtr = tdop[i]                       #  --//--

    for i in range(len(L1)):
# Здесь подбирается радиатор из сетки размеров для одной и двх сторон
        if k == 1:
            l = L1[i]
            b = B1[i]
        else:
            l = L2[i]
            b = B2[i]
# Если радиатор из списка больше допустимого размера, значит подборки нет
    if (l > lm) or (b > bm):
        print("Финита ля комедия. Радиаторов не существует. Это фантастика")
        break

    n1 = (l - 0.008)/s + 1
    n2 = (b - 0.008)/s + 1
    nz = n1 * n2

    fp = l * b
#    gpr = number_Gr(tb, dtr, l)
    nu_plane = number_Nu_plane(tb, dtr, l)
    alfp = number_Alfa(nu_plane, l)

    fs = 3.14 * d * h1 * nz - fs1
    if fs < 0:
        fs = 0

    pp = alfp * fp * dtr
    a4 = (d / s) ** 1.7
    a1 = 1.83E-6 * a4 * (5.7 + 0.22* n1) / d
    a2 = 0.11 * a4 * n1
    fv = 1200 * h1 * b  # ???
    dp = 0
    dh = 0
    dtv = dtr + 0.1
    if dp > dh:
        dtv = dtv +0.1
    if dr <= dh:
        dtv = dtv - 0.1

    gr = number_Gr(tb, (dtr-dtv/2), d)
    nus = 0.236 * gr ** 0.125
    alfs = number_Alfa(nus, d)
    ps = alfs * fs * (dtr - dtv/2)
    w = ps / (fv * dtv)
    dp = w * (a1 + a2 * w)
    dh = 0.6 * l * dtv / (273 + tb + dtv/2)
    a3 = (abs(dp - dh)/dh)
    if a3 <= 0.1:
        f0 = l * b - 0.785 * d ** 2 * nz
        p0 = alfp * f0 * dtr
        tr = tb + dtr
if __name__ == '__main__':
    main()
