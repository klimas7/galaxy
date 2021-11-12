import random

from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Line, Quad, Triangle
from kivy.graphics.context_instructions import Color
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget


class MainWidget(Widget):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = .2
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = .1
    horizontal_lines = []

    SPEED = 4
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 12
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tiles_coordination()
        self.generate_tiles_coordinates()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    @staticmethod
    def is_desktop():
        return platform in ('linux', 'win', 'macosx')

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def pre_fill_tiles_coordination(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        # clean the coordinate that are out of the screen
        # ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        begin_x_index = -int(self.V_NB_LINES / 2) + 1
        end_x_index = begin_x_index + self.V_NB_LINES - 1

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(-1, 1)
            # -1 -> left
            # 0 -> straight
            # 1 -> left
            if last_x >= end_x_index - 1:
                r = -1
            if last_x <= begin_x_index:
                r = 1

            self.tiles_coordinates.append((last_x, last_y))
            if r != 0:
                last_x += r
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1

    def get_line_x_from_index(self, index):
        center_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = center_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        return index * spacing_y - self.current_offset_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_vertical_lines(self):
        begin_x_index = -int(self.V_NB_LINES/2) + 1
        end_x_index = begin_x_index + self.V_NB_LINES
        for i in range(begin_x_index, end_x_index):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        begin_x_index = -int(self.V_NB_LINES / 2) + 1
        end_x_index = begin_x_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(begin_x_index)
        xmax = self.get_line_x_from_index(end_x_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            ti_x, ti_y = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
            xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_ship(self):
        base_y = self.SHIP_BASE_Y * self.height
        ship_width = (self.SHIP_WIDTH / 2) * self.width

        tr_x_1, tr_y_1 = (self.perspective_point_x - ship_width, base_y)
        tr_x_2, tr_y_2 = (self.perspective_point_x, base_y + self.SHIP_HEIGHT*self.height)
        tr_x_3, tr_y_3 = (self.perspective_point_x + ship_width, base_y)
        x1, y1 = self.transform(tr_x_1, tr_y_1)
        x2, y2 = self.transform(tr_x_2, tr_y_2)
        x3, y3 = self.transform(tr_x_3, tr_y_3)
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        self.current_offset_y += self.SPEED * time_factor

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            self.generate_tiles_coordinates()

        self.current_offset_x += self.current_speed_x * time_factor


class GalaxyApp(App):
    pass


GalaxyApp().run()
