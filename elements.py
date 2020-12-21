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


class ElectronicElement():
    """
    Электрический элемент.
    param:
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

    SV = [0, 1E-2, 3E-2, 5E-2, 7.2E-2, 1.05E-1, 1.4E-1]

    def __init__(self, power, max_t, contact_space, temp_resist, viborka):
        self.power = power
        self.max_t = max_t
        self.contact_space = contact_space
        self.temp_resist = temp_resist
        self.viborka = int(viborka)


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
        param:
            air_temp : float
                Температура окружающей среды (среды охлаждения)

        Возвращает допустимый перегрев элемента относительно окружающей среды [*C]
        dTдоп = Tmax - t.air * P * sigmaT / S.контакта
        """
        return self.max_t - air_temp - self.power * self.temp_resist / self.contact_space


    def fr1_exclude_surface(self, fin_height):
        """
        param:
            fin_height : float
                Высота ребра используемого радиатора [м]

        Возвращает площадь боковой поверхности рёбер радиатора, изымаемая при установке
        элемента на ребристую сторону радиатора. Рассчитывается исходя из
        признака выборки по РД5.8794-88 (или ОСТ) [м^2]
        """
        return 2 * self.SV[self.viborka] * fin_height


class SetElectronicElements():
    """
    Набор элементов на одном радиаторе.

    params:
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

        params:
            element : <ElectronicElement>
                Объект класса <ElectronicElement>
        """
        self.pull.append(element)


    def dtr_permissible_overheating(self, air_temp):
        """
        Возвращает минимальное значение допустимого перегрева для набора элементов
        на радиаторе.

        params:
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


def main():
    pass

if __name__ == '__main__':
    main()
