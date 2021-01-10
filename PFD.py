
# -*- coding: utf-8 -*-

from remi import gui
from remi import start, App


class AttitudeIndicator(gui.SvgSubcontainer):
    def __init__(self, *args, **kwargs):
        gui.SvgSubcontainer.__init__(self, -0.5, -0.5, 1, 1, *args, **kwargs)

        self.attr_viewBox = "-0.5 -0.5 1.0 1.0"

        
        self.group_pitch = gui.SvgGroup()
        self.group_pitch.css_transform = "rotate(0deg), translate(0, 0)"
        self.group_pitch.css_transform_box = "fill-box"
        self.group_pitch.css_transform_origin = "center"
        
        self.group_roll = gui.SvgGroup()
        self.group_roll.css_transform = "rotate(0deg), translate(0, 0)"
        self.group_roll.css_transform_box = "fill-box"
        self.group_roll.css_transform_origin = "center"
        self.group_roll.append(self.group_pitch)

        #considering an Attitude Indicator 200x200, measures are in parts of 1

        #horizon
        #background is static and occupy the entire attidute indicator
        self.horizon_background = gui.SvgRectangle(-0.5, -0.5, 1, 1)
        self.horizon_background.set_fill("rgb(0,100,255)")
        self.append(self.horizon_background)

        self.horizon_terrain = gui.SvgRectangle(-1, 0, 2, 2)
        self.horizon_terrain.set_fill("rgb(151,53,0)")
        self.horizon_terrain.set_stroke(0.01, "lightgray")
        self.group_pitch.append(self.horizon_terrain)

        self.append(self.group_roll)

        #airplaine indicator is steady
        thick = 0.02
        self.airplane_svg_left = gui.SvgPolygon(8)
        self.airplane_svg_left.set_fill('gray')
        self.airplane_svg_left.set_stroke(1, 'black')
        self.airplane_svg_left.add_coord(-0.2, 0) #25x8
        self.airplane_svg_left.add_coord(-0.45, 0)
        self.airplane_svg_left.add_coord(-0.45, thick)
        self.airplane_svg_left.add_coord(-0.2 - thick, thick)
        self.airplane_svg_left.add_coord(-0.2 - thick, thick + 0.08)
        self.airplane_svg_left.add_coord(-0.2, thick + 0.08)
        self.airplane_svg_left.add_coord(-0.2, 0.08)

        self.airplane_svg_right = gui.SvgPolygon(8)
        self.airplane_svg_right.set_fill('gray')
        self.airplane_svg_right.set_stroke(1, 'black')
        self.airplane_svg_right.add_coord(0.2, 0) #25x8
        self.airplane_svg_right.add_coord(0.45, 0)
        self.airplane_svg_right.add_coord(0.45, thick)
        self.airplane_svg_right.add_coord(0.2 + thick, thick)
        self.airplane_svg_right.add_coord(0.2 + thick, thick + 0.08)
        self.airplane_svg_right.add_coord(0.2, thick + 0.08)
        self.airplane_svg_right.add_coord(0.2, 0.08)

        self.airplane_svg_center = gui.SvgRectangle(-0.02, -0.02, 0.04, 0.04)
        self.airplane_svg_center.set_fill('white')
        self.airplane_svg_center.set_stroke(0.01, 'lightgray')

        self.append([self.airplane_svg_left, self.airplane_svg_right, self.airplane_svg_center])

    
        

class PrimaryFlightDisplay(gui.Svg):
    def __init__(self, *args, **kwargs):
        gui.Svg.__init__(self, *args, **kwargs)
        self.attr_viewBox = "-0.5 -0.5 1.0 1.0"
        self.attitude_indicator = AttitudeIndicator()
        self.append(self.attitude_indicator)

    def set_attitude_pitch(self, value):
        pass
    def set_attitude_roll(self, value):
        pass
    def set_attitude_orientation(self, value):
        pass

class Application(App):
    def idle(self):
        #idle function called every update cycle
        #self.svg_group.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.rotation, self.movement)
        pass

    def main(self):
        vbox0 = gui.VBox()

        self.pfd = PrimaryFlightDisplay(width=200, height=200)
        vbox0.append(self.pfd)

        return vbox0
    
    def onchange_slider_rotate(self, emitter, value):
        self.rotation = value

    def onchange_slider_movement(self, emitter, value):
        self.movement = value


#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    start(Application, multiple_instance=False, start_browser=True)
