# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        модуль1
# Purpose:
#
# Author:      g.ukryukov
#
# Created:     21.12.2020
# Copyright:   (c) g.ukryukov 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------


class FinnedRadiator():
    """
    Ребристый радиатор.
    param:
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


    >>> rad = FinnedRadiator(length=35E-3, width=30E-3, fin_height=0.01, step=0.01, base_thick=0.004, fin_thick=0.001)
    >>> rad.edge_number()
    3.0
    >>> round(rad.flat_surface(), 7)
    0.00105
    >>> round(rad.half_step(), 7)
    0.0045
    >>> round(rad.fins_surface(), 7)
    0.0014
    >>> round(rad.equal_diameter(), 7)
    0.0094737
    """
    def __init__(self, length, width, fin_height, step=10E-3, base_thick=4E-3, fin_thick=1E-3):
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
        params:
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


    def equal_diameter(self):
        """
        Возвращает эквивалентный диаметр для течения среды в каналах рёбер
        dell - половина расстояния между рёбрами, h1 - высота ребра
        На выходе Real
        """
        dell = self.half_step()
        h1 = self.fin_height

        area = 2 * dell * h # площадь канала между рёбрами
        perimeter = 2 * (h1 + 2 * dell) # периметр канала между рёбрами
        return 4 * area / perimeter


def fin_radiator_generator(k=1, length=0.01, max_width=0.5, step = 0.01):
    """
    param:
        k : integer
            Количество оребрённых сторон у радиатора. 1-Односторонний ОСТ радиатор,
            2 - двусторонний ГОСТ радиатор, 0 - односторонний кастомный радиатор
            с фиксированной длиной ребра
        length : float
            Фиксированная длина ребра кастомного радиатора
        max_width: float
            Максимально допустимая ширина кастомного радиатора
        step : float
            Шаг увеличения ширины (шаг ребра, чтоб увеличивать ширину на одно ребро)
    Возвращает список параметров радиатора (длину и ширину) с шагом ширины step в формате [[l1, b1], [l1, b2],...]

    >>> a = fin_radiator_generator()
    >>> print(a)
    [[0.036, 0.032], [0.036, 0.072], [0.05, 0.032], [0.05, 0.052], [0.05, 0.092], [0.08, 0.032], [0.08, 0.072], [0.08, 0.122], [0.1, 0.052], [0.1, 0.092], [0.1, 0.152], [0.125, 0.072], [0.125, 0.122], [0.125, 0.152]]
    >>> print(fin_radiator_generator(2))
    [[0.05, 0.052], [0.05, 0.092], [0.08, 0.072], [0.08, 0.122], [0.1, 0.052], [0.1, 0.092], [0.1, 0.152], [0.125, 0.072], [0.125, 0.122], [0.125, 0.152]]
    >>> print(fin_radiator_generator(0, 0.01, 0.14))
    [[0.01, 0.01], [0.01, 0.02], [0.01, 0.03], [0.01, 0.04], [0.01, 0.05], [0.01, 0.06], [0.01, 0.07], [0.01, 0.08], [0.01, 0.09], [0.01, 0.1], [0.01, 0.11], [0.01, 0.12], [0.01, 0.13]]
    """

    L1 = [3.6E-2, 3.6E-2, 5E-2, 5E-2, 5E-2, 8E-2, 8E-2, 8E-2, 1E-1, 1E-1,  1E-1,
            1.25E-1, 1.25E-1, 1.25E-1]
    B1 = [3.2E-2, 7.2E-2, 3.2E-2, 5.2E-2, 9.2E-2, 3.2E-2, 7.2E-2, 1.22E-1,
            5.2E-2, 9.2E-2, 1.52E-1, 7.2E-2, 1.22E-1, 1.52E-1]
    one_side_standart_radiator = [list(el) for el in zip(L1, B1)]

    L2 = [5E-2, 5E-2, 8E-2, 8E-2, 1E-1, 1E-1, 1E-1, 1.25E-1, 1.25E-1,  1.25E-1]
    B2 = [5.2E-2, 9.2E-2, 7.2E-2, 1.22E-1, 5.2E-2, 9.2E-2, 1.52E-1, 7.2E-2,
            1.22E-1, 1.52E-1]
    two_side_standart_radiator = [list(el) for el in zip(L2, B2)]

    custom_radiator = [[length, i*step] for i in range(1, int(max_width/step))]

    radiators = {1:one_side_standart_radiator, 2:two_side_standart_radiator, 0:custom_radiator}
    return radiators[k]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
