
init python early in _stats_gui:

    import sys
    import math
    import store
    import pygame_sdl2 as pygame
    from store import (
        config,
        _0some_utils as _some_utils
    )


    VERSION = (1, 0, 0)

    class StatsDiag(renpy.Displayable, store.NoRollback):

        __author__ = "Vladya"

        def __init__(self, *values, **kwargs):
            """

            Класс принимает параметры, которые будут показаны на диаграмме.

            Параметр может быть передан числовым значением
                (будет приведён к float)

            Либо кортежом:
                (числовое_значение, текстовая_метка)
                Параметры текстовых меток могут быть переданы с префиксом
                    :text_:


            Опциональный параметр :max_value:
                (float / int)

                Если передан,
                    то максимальное значение диаграммы будет установлено.

                Если не передан,
                    то максимальное значение будет рассчитано по максимальному
                    числовому значению.


            Опциональный параметр :diag_color:
                (любой формат цвета)

                Цвет диаграммы.
                Если не передан - чёрный.


            Опциональный параметр :radius:
                (float)

                Радиус диаграммы (в пикселях).
                Если не указано - половина золотого сечение от ширины экрана.


            Примеры:

                StatsDiag((1., "Сила"), (7, "Ловкость"))

                    Диаграмма с двумя именованными параметрами,
                    где максимальное значение будет установлено на 7.
                    Цвет чёрный.


                StatsDiag(7, 6, 8, 10)

                    Диаграмма с 4 неименованными параметрами,
                    где максимальное значение будет установлено на 10.
                    Цвет чёрный.


                StatsDiag((1., "Сила"), 6, 8, (7, "Ловкость"))

                    Диаграмма с 4 смешанными параметрами,
                    где максимальное значение будет установлено на 8.
                    Именованные параметры будут подписаны, остальные - нет.
                    Цвет чёрный.


                StatsDiag((1., "Сила"), 6, 8, max_value=100, color="#0f0")

                    Диаграмма с 3 смешанными параметрами,
                    где максимальное значение будет установлено на 100.
                    Именованные параметры будут подписаны, остальные - нет.
                    Цвет зелёный.


                StatsDiag((1., "Сила"), 6, 8, max_value=100, text_size=50)

                    Диаграмма с 3 смешанными параметрами,
                    где максимальное значение будет установлено на 100.
                    Именованные параметры будут подписаны, остальные - нет.
                    Цвет чёрный.

                    Размер текста, переданный через префикс `text_`,
                    будет установлен на 50.

            """

            self.__text_properties, kwargs = renpy.split_properties(
                kwargs,
                "text_",
                ""
            )
            max_value = kwargs.pop("max_value", None)
            if max_value is not None:
                max_value = abs(float(max_value))

            color = renpy.color.Color(kwargs.pop("diag_color", "#000"))
            polygon_color = renpy.color.Color(
                kwargs.pop("polygon_color", "#000")
            )
            polygon_width = kwargs.pop("polygon_width", 3)

            radius = kwargs.pop("radius", None)
            if radius is None:
                radius = (float(config.screen_height) * _some_utils.PHI2) / 2.
            radius = float(radius)

            super(StatsDiag, self).__init__(**kwargs)

            self.__values = ()
            for value in values:
                self.add_value(value, False)

            self.__max_value = max_value
            self.__color = color
            self.__radius = radius

            self.__polygon_color = polygon_color
            self.__polygon_width = polygon_width

            self.__offset = .0

            self.__coors = _list()

        def _clear(self):
            self.__values = ()
            renpy.redraw(self, .0)

        def add(self, child):
            if not isinstance(child, _PseudoDisp):
                raise TypeError("`_PseudoDisp` only")
            self.add_value(child)

        def per_interact(self):
            renpy.redraw(self, .0)

        def event(self, ev, x, y, st):
            for disp, (disp_x, disp_y) in self.__coors:
                ev_x = x - disp_x
                ev_y = y - disp_y
                disp.event(ev, ev_x, ev_y, st)

        def add_value(self, value):

            disp = None
            if isinstance(value, _PseudoDisp):
                if value not in self.__values:
                    value.set_text_props(self.__text_properties)
                    self.__values += (value,)
                renpy.redraw(self, .0)
                return

                # ###
                self.__values += ((value, disp),)

                if value in self.__pseudo_disps:
                    if redraw:
                        renpy.redraw(self, .0)
                    return

                self.__pseudo_disps.append(value)
                disp = value._get_child()
                if not disp:
                    value = float(value._value)
                    if value.is_integer():
                        value = int(value)
                    disp = _some_utils.unicode(value)
                value = (value._value, disp)

            disp = None
            if isinstance(value, (_list, tuple)):
                value, disp = value

            value = _PseudoDisp(
                abs(float(value)),
                text_props=self.__text_properties
            )
            if disp is not None:
                value.add(disp)

            self.__values += (value,)
            renpy.redraw(self, .0)

        def get_max_value(self):
            if self.__max_value is not None:
                return abs(float(self.__max_value))
            max_value = None
            for pseudo_disp in self.__values:
                if (max_value is None) or (pseudo_disp._value > max_value):
                    max_value = pseudo_disp._value
            return max_value

        @property
        def _offset(self):
            return self.__offset

        @_offset.setter
        def _offset(self, new_offset):
            self.__offset = (float(new_offset) % 1.)
            renpy.redraw(self, .0)

        @staticmethod
        def circle_func(radius, state, offset=.0):
            """

            "Оторисовывает" круг с радиусом :radius:
            и возвращает координату на этапе :state:

            Круг будет прижат к координате (0, 0) в положительную плоскость.
            Отрисовка производится по часовой стрелке.


            :radius:
                Радиус нужного круга.
                Положительное число.

            :state:
                Этап отрисовки.
                float значение от .0, до 1.

            """

            radius = abs(float(radius))
            state = float(state)

            state += .25  # Чтобы отрисовка начиналась с крайней верхней точки.
            state += offset
            state %= 1.
            assert (.0 <= state < 1.)

            # Нужный угол.
            angle = (2. * math.pi) * state

            # т.к. радиус - это и есть гипотенуза. Для читаемости.
            _hypot = radius

            # Косинус умножаем на гипотенузу, для получения прилежащего катета.
            # (Координата оси абсцисс)
            _cos = math.cos(angle) * (-1.)  # Инвертируем вращение.
            _sin = math.sin(angle) * (-1.)
            xrelative = _cos * _hypot
            yrelative = _sin * _hypot

            x = radius + xrelative
            y = radius + yrelative

            return (x, y)

        def visit(self):
            rv = []
            for pseudo_disp in self.__values:
                rv.extend(pseudo_disp.visit())
            return rv

        def render(self, *rend_args):

            d = self.__radius * 2.
            result_size = d + (d * _some_utils.PHI)
            result = renpy.Render(*map(int, (result_size, result_size)))

            canvas_rend = renpy.Render(*map(int, (d, d)))
            canvas = canvas_rend.canvas()

            points_len = len(self.__values)

            max_polygon_coor = []
            points = []
            disps = []
            max_value = self.get_max_value()
            for i, pseudo_disp in enumerate(self.__values):

                disps.append(pseudo_disp._get_child())

                _place = float(i) / float(points_len)
                x, y = self.circle_func(self.__radius, _place, self._offset)
                max_polygon_coor.append(tuple(map(int, (x, y))))

                calc_value = min(max(pseudo_disp._value, .0), max_value)
                try:
                    state = calc_value / max_value
                except ZeroDivisionError:
                    state = .0
                path_x = x - self.__radius
                path_y = y - self.__radius

                point = (
                    (self.__radius + (path_x * state)),
                    (self.__radius + (path_y * state))
                )
                points.append(tuple(map(int, point)))

            canvas.polygon(
                self.__polygon_color,
                max_polygon_coor,
                self.__polygon_width
            )

            canvas.polygon(self.__color, points)

            xpos = (result_size * .5) - (d * .5)
            ypos = (result_size * .5) - (d * .5)
            result.blit(canvas_rend, tuple(map(int, (xpos, ypos))))

            _coors = _list()
            for disp, (x, y) in zip(disps, max_polygon_coor):

                if not disp:
                    continue

                xalign = float(x) / d
                yalign = float(y) / d

                rend = renpy.render(disp, *rend_args)
                xsize, ysize = map(float, rend.get_size())

                xpos = (result_size * xalign) - (xsize * xalign)
                ypos = (result_size * yalign) - (ysize * yalign)
                pos = tuple(map(int, (xpos, ypos)))

                _coors.append((disp, pos))
                result.blit(rend, tuple(map(int, pos)))

            self.__coors = _coors

            return result


    class _PseudoDisp(store.Null, store.NoRollback):

        __author__ = "Vladya"

        def __init__(self, value, **kwargs):
            super(_PseudoDisp, self).__init__()
            self.__text_properties = kwargs.pop("text_props", None)
            self.__stat_value = float(value)
            self.__cached_child = None
            self.__child = None

        def visit(self):
            return [self._get_child()]

        def per_interact(self):
            self.__cached_child = None
            renpy.redraw(self, .0)

        def _clear(self):
            self.__child = None
            self.__cached_child = None
            renpy.redraw(self, .0)

        def add(self, child):
            if isinstance(child, renpy.display.layout.Container):
                if (not child.children) and (not child.child):
                    child = None
            if child is not None:
                self.__child = _some_utils.get_displayable(child)
                self.__cached_child = None
            renpy.redraw(self, .0)

        def set_text_props(self, props=None):
            self.__text_properties = props
            self.__cached_child = None
            renpy.redraw(self, .0)

        def _get_child(self):

            if not self.__cached_child:

                if self.__child:
                    self.__cached_child = self.__child
                else:
                    value = float(self._value)
                    if value.is_integer():
                        value = int(value)

                    value = _some_utils.unicode(value)

                    if not isinstance(value, _some_utils.basestring):
                        raise RuntimeError("Некорректный тип.")

                    if isinstance(value, bytes):
                        value = value.decode("utf_8", "ignore")

                    _kw = (self.__text_properties or _dict())
                    self.__cached_child = store.Text(value, **_kw)

            return self.__cached_child

        @property
        def _value(self):
            return self.__stat_value


    _reg = renpy.register_sl_displayable(
        "stat_diagram",
        StatsDiag,
        "fixed",
        "many",
        default_properties=True
    )

    _reg = _reg.add_property("max_value")
    _reg = _reg.add_property("radius")

    _reg = _reg.add_property("diag_color")

    _reg = _reg.add_property("polygon_color")
    _reg = _reg.add_property("polygon_width")

    _reg = _reg.add_property_group("text", "text_")


    _child_reg = renpy.register_sl_displayable(
        "stat",
        _PseudoDisp,
        "fixed",
        1,
        default_properties=False
    )
    _child_reg = _child_reg.add_positional("value")
