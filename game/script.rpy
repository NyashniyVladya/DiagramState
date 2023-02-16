
# Тесты.

screen test1:

    default _values = list(map(lambda _i: renpy.random.randint(5, 15), range(7)))

    vbox:
        align (.5, .5)
        stat_diagram:
            diag_color (252, 224, 169)
            polygon_color (204, 145, 91)
            max_value 30
            for i, v in enumerate(_values):
                stat v:
                    vbox:
                        text "Stat: [v]" color (184, 180, 176)
                        hbox:
                            textbutton '+':
                                action SetDict(_values, i, (v + 1))
                            textbutton '-':
                                action SetDict(_values, i, (v - 1))
        textbutton "Вернуться":
            action Return()

screen test2:
    vbox:
        align (.5, .5)
        stat_diagram:
            diag_color "#0f0"
            polygon_color "#00f"
            polygon_width 5
            stat 1
            stat 5
            stat 11
            stat 15
            stat 2
        textbutton "Вернуться":
            action Return()

screen test3:

    vbox:
        align (.5, .5)
        stat_diagram:
            radius 100
            text_size 12
            stat 12
            stat 62
            stat 73:
                null  # Ничего не писать.
            stat 24
            stat 50:
                text "Some text" size 12
            stat 16
        textbutton "Вернуться":
            action Return()

label start:

    scene expression "#555"
    while True:
        menu:
            "Тест №1. 7 элементов":
                call screen test1
            "Тест №2. 5 элементов":
                call screen test2
            "Тест №3. 6 элементов":
                call screen test3

    return
