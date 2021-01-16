
# -*- coding: utf-8 -*-

from remi import gui
from remi import start, App
import math

class AttitudeIndicator(gui.SvgSubcontainer):
    pitch = 0
    orientation = 0
    roll = 0

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
        self.group_roll.css_transform_origin = "50% 19%"
        self.group_roll.append(self.group_pitch)

        #considering an Attitude Indicator 200x200, measures are in parts of 1

        #roll and bank indicator
        self.group_roll_and_bank_angle_indicator = gui.SvgGroup()
        self.roll_indicator = gui.SvgPolygon(3)
        self.roll_indicator.set_fill('transparent')
        self.roll_indicator.set_stroke(1, 'black')
        self.roll_indicator.add_coord(-0.04, -0.44)
        self.roll_indicator.add_coord(0.0, -0.44 - 0.03)
        self.roll_indicator.add_coord(0.04, -0.44)
        self.group_roll_and_bank_angle_indicator.append(self.roll_indicator)
        self.bank_indicator = gui.SvgPolygon(4)
        self.bank_indicator.set_fill('transparent')
        self.bank_indicator.set_stroke(1, 'black')
        self.bank_indicator.add_coord(-0.04, -0.44)
        self.bank_indicator.add_coord(0.04, -0.44)
        self.bank_indicator.add_coord(0.04, -0.44 + 0.02)
        self.bank_indicator.add_coord(-0.04, -0.44 + 0.02)
        self.group_roll_and_bank_angle_indicator.append(self.bank_indicator)
        self.group_roll.append(self.group_roll_and_bank_angle_indicator)

        #horizon
        #background is static and occupy the entire attidute indicator
        self.horizon_background = gui.SvgRectangle(-0.5, -0.5, 1, 1)
        self.horizon_background.set_fill("rgb(0,100,255)")
        self.append(self.horizon_background)

        self.horizon_terrain = gui.SvgRectangle(-1, 0, 2, 2)
        self.horizon_terrain.set_fill("rgb(151,53,0)")
        self.horizon_terrain.set_stroke(0.01, "lightgray")
        self.group_pitch.append(self.horizon_terrain)


        #pitch angle indication
        s1 = 0.2 #min_sign_width
        s2 = 0.3 #mid_sign_width
        s3 = 0.5 #max_sign_width
        sign_y_offset = 0.03
        angle_step_list = [30, 27.5, 25, 22.5, 20, 17.5, 15, 12.5, 10, 7.5, 5, 2.5, 0, -2.5, -5, -7.5, -10, -12.5, -15, -17.5, -20, -22.5, -25, -27.5, -30]
        sign_sizes =      [s3,   s1, s2,   s1, s3,   s1, s2,   s1, s3,  s1, s2, s1, 0,   s1, s2,   s1,  s3,    s1,  s2,    s1,  s3,    s1,  s2,    s1,  s3]        
        for i in range(0, len(angle_step_list)):
            angle_step = angle_step_list[i]
            sign_size = sign_sizes[i]
            line = gui.SvgLine(-sign_size/2, angle_step*sign_y_offset, sign_size/2, angle_step*sign_y_offset)
            line.set_stroke(0.01, 'white')
            self.group_pitch.append(line)


        self.append(self.group_roll)


        #roll angle indication
        min_radius = 0.45
        mid_radius = 0.48
        max_radius = 0.5
        n_divisions = 14
        for step in range(0, n_divisions+1):
            a = ((180/n_divisions)*step)/180*math.pi
            r = min_radius if (step%2)==1 else mid_radius
            line = gui.SvgLine(math.cos(a)*r, -math.sin(a)*r, math.cos(a)*max_radius, -math.sin(a)*max_radius)
            line.set_stroke(0.01, 'black')
            self.append(line)


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

    def set_pitch(self, pitch):
        self.pitch = pitch
        
    def set_orientation(self, orientation):
        self.orientation = orientation
        
    def set_roll(self, roll):
        self.roll = roll

    def update_attitude(self):
        self.group_pitch.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.orientation, self.pitch)
        self.group_roll.attributes['transform'] = "rotate(%s 0 0)"%(self.roll)
        self.horizon_terrain.attributes['transform'] = "translate(0 %s)"%self.pitch
                

class PrimaryFlightDisplay(gui.Svg):
    def __init__(self, *args, **kwargs):
        gui.Svg.__init__(self, *args, **kwargs)
        self.attr_viewBox = "-0.5 -0.5 1.0 1.0"
        self.attitude_indicator = AttitudeIndicator()
        self.append(self.attitude_indicator)

    def set_attitude_pitch(self, value):
        self.attitude_indicator.set_pitch(value)

    def set_attitude_orientation(self, value):
        self.attitude_indicator.set_orientation(value)

    def set_attitude_roll(self, value):
        self.attitude_indicator.set_roll(value)

    def update_attitude(self):
        self.attitude_indicator.update_attitude()


class Application(App):
    def idle(self):
        #idle function called every update cycle
        #self.svg_group.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.rotation, self.movement)
        self.pfd.set_attitude_pitch(float(self.slider_pitch.get_value()))
        self.pfd.set_attitude_orientation(float(self.slider_orientation.get_value()))
        self.pfd.set_attitude_roll(float(self.slider_roll.get_value()))
        self.pfd.update_attitude()

    def main(self):
        vbox0 = gui.VBox()

        self.pfd = PrimaryFlightDisplay(width=200, height=200)
        vbox0.append(self.pfd)

        self.slider_pitch = gui.SpinBox(0, -1.0, 1.0, 0.01)
        self.slider_orientation = gui.SpinBox(0, -100, 100, 1)
        self.slider_roll = gui.SpinBox(0, -100, 100, 1)

        vbox0.append( gui.HBox(children=[gui.Label('pitch'), self.slider_pitch]) )
        vbox0.append( gui.HBox(children=[gui.Label('orientation'), self.slider_orientation]) )
        vbox0.append( gui.HBox(children=[gui.Label('roll'), self.slider_roll]) )

        return vbox0
    


#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    start(Application, multiple_instance=False, start_browser=True, debug=False)
