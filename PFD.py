
# -*- coding: utf-8 -*-

from remi import gui
from remi import start, App
import math

class AttitudeIndicator(gui.SvgSubcontainer):
    pitch = 0
    orientation = 0
    roll = 0

    pitch_roll_scale_limit = 60

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
        self.group_roll.css_transform_origin = "50% 20%"
        self.group_roll.append(self.group_pitch)

        #horizon
        #background is static and occupy the entire attidute indicator
        self.horizon_background = gui.SvgRectangle(-0.5, -0.5, 1, 1)
        self.horizon_background.set_fill("rgb(0,100,255)")
        self.append(self.horizon_background)

        self.group_horizon_terrain = gui.SvgGroup()
        self.horizon_terrain = gui.SvgRectangle(-1, 0, 2, 2)
        self.horizon_terrain.set_fill("rgb(53, 151, 0)")
        self.horizon_terrain.set_stroke(0.001, "lightgray")
        self.group_horizon_terrain.append(self.horizon_terrain)
        self.append(self.group_horizon_terrain)

        #pitch angle indication
        self.group_pitch_indicator = gui.SvgGroup()
        self.group_pitch.append(self.group_pitch_indicator)
        self.generate_pitch_indicator()

        self.append(self.group_roll)


        #roll angle indication
        min_radius = 0.46
        mid_radius = 0.48
        max_radius = 0.5
        angle_min = -60
        angle_max = 60
        angle_step = 5
        self.group_roll_indicator = gui.SvgGroup()
        for angle in range(angle_min, angle_max+angle_step, angle_step):
            r = min_radius if (angle%10)==0 else mid_radius
            x_min = math.cos(math.radians(angle+90))*r
            y_min = -math.sin(math.radians(angle+90))*r
            x_max = math.cos(math.radians(angle+90))*max_radius
            y_max = -math.sin(math.radians(angle+90))*max_radius
            
            hide_scale = abs(int(angle))>self.pitch_roll_scale_limit

            line = gui.SvgLine(x_min, y_min, x_max, y_max)
            line.set_stroke(0.01, 'white' if not hide_scale else 'transparent')
            self.group_roll_indicator.append(line)
            if (angle%10)==0:
                x_txt = math.cos(math.radians(angle+90))*(min_radius-0.03)
                y_txt = -math.sin(math.radians(angle+90))*(min_radius-0.03)
                txt = gui.SvgText(x_txt, y_txt, str(abs(int(angle))))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'middle'
                txt.set_fill('white' if not hide_scale else 'transparent')
                txt.css_font_size = '0.04px'
                txt.css_font_weight = 'bolder'
                self.group_roll_indicator.append(txt)
        self.append(self.group_roll_indicator)


        #roll and bank indicator
        self.group_roll_and_bank_angle_indicator = gui.SvgGroup()
        self.roll_indicator = gui.SvgPolygon(3)
        self.roll_indicator.set_fill('red')
        self.roll_indicator.set_stroke(1, 'black')
        self.roll_indicator.add_coord(-0.04, -0.06)
        self.roll_indicator.add_coord(0.0, -0.06 - 0.03)
        self.roll_indicator.add_coord(0.04, -0.06)
        self.group_roll_and_bank_angle_indicator.append(self.roll_indicator)
        self.bank_indicator = gui.SvgPolygon(4)
        self.bank_indicator.set_fill('transparent')
        self.bank_indicator.set_stroke(1, 'black')
        self.bank_indicator.add_coord(-0.04, -0.06 + 0.005)
        self.bank_indicator.add_coord(0.04, -0.06 + 0.005)
        self.bank_indicator.add_coord(0.04, -0.06 + 0.025)
        self.bank_indicator.add_coord(-0.04, -0.06 + 0.025)
        self.group_roll_and_bank_angle_indicator.append(self.bank_indicator)
        self.group_roll_and_bank_angle_indicator.attributes['transform'] = "translate(0 -0.30)"
        self.append(self.group_roll_and_bank_angle_indicator)

        #airplaine indicator is steady
        thick = 0.02
        self.airplane_svg_left = gui.SvgPolygon(8)
        self.airplane_svg_left.set_fill('gray')
        self.airplane_svg_left.set_stroke(1, 'black')
        self.airplane_svg_left.add_coord(-0.2, 0) #25x8
        self.airplane_svg_left.add_coord(-0.40, 0)
        self.airplane_svg_left.add_coord(-0.40, thick)
        self.airplane_svg_left.add_coord(-0.2 - thick, thick)
        self.airplane_svg_left.add_coord(-0.2 - thick, thick + 0.08)
        self.airplane_svg_left.add_coord(-0.2, thick + 0.08)
        self.airplane_svg_left.add_coord(-0.2, 0.08)

        self.airplane_svg_right = gui.SvgPolygon(8)
        self.airplane_svg_right.set_fill('gray')
        self.airplane_svg_right.set_stroke(1, 'black')
        self.airplane_svg_right.add_coord(0.2, 0) #25x8
        self.airplane_svg_right.add_coord(0.40, 0)
        self.airplane_svg_right.add_coord(0.40, thick)
        self.airplane_svg_right.add_coord(0.2 + thick, thick)
        self.airplane_svg_right.add_coord(0.2 + thick, thick + 0.08)
        self.airplane_svg_right.add_coord(0.2, thick + 0.08)
        self.airplane_svg_right.add_coord(0.2, 0.08)

        self.airplane_svg_center = gui.SvgRectangle(-0.02, -0.02, 0.04, 0.04)
        self.airplane_svg_center.set_fill('white')
        self.airplane_svg_center.set_stroke(0.01, 'lightgray')

        self.append([self.airplane_svg_left, self.airplane_svg_right, self.airplane_svg_center])

        self.generate_orientation_indicator()

    def generate_orientation_indicator(self):
        self.group_orientation_indicator_with_pointer = gui.SvgGroup()
        
        orientation_indicator_y_pos = 0.3

        #orientation angle indication
        min_radius = 0.3
        mid_radius = 0.32
        max_radius = 0.35
        angle_min = -180
        angle_max = 180
        angle_step = 5
        self.group_orientation_indicator = gui.SvgGroup()
        labels = {0:'N', -45:'NE', -90:'E', -135:'SE', -180:'S', 180:'S', 135:'SW', 90:'W', 45:'NW'}
        circle = gui.SvgCircle(0,0, max_radius)
        circle.set_fill('rgba(0,0,0,0.3)')
        circle.set_stroke(0.01, 'white')
        self.group_orientation_indicator.append(circle)
        for angle in labels.keys():
            r = min_radius
            x_min = math.cos(math.radians(angle+90))*r
            y_min = -math.sin(math.radians(angle+90))*r
            x_max = math.cos(math.radians(angle+90))*max_radius
            y_max = -math.sin(math.radians(angle+90))*max_radius

            line = gui.SvgLine(x_min, y_min, x_max, y_max)
            line.set_stroke(0.01, 'white')
            self.group_orientation_indicator.append(line)

            x_txt = math.cos(math.radians(angle+90))*(min_radius-0.03)
            y_txt = -math.sin(math.radians(angle+90))*(min_radius-0.03)
            txt = gui.SvgText(x_txt, y_txt, labels.get(angle, ''))
            txt.attr_dominant_baseline = 'middle'
            txt.attr_text_anchor = 'middle'
            txt.set_fill('white')
            txt.css_font_size = '0.07px'
            txt.css_font_weight = 'bolder'
            txt.css_transform_origin = '50% 50%'
            txt.css_transform_box = 'fill-box'
            txt.attributes['transform'] = 'rotate(%s)'%(-angle)
            self.group_orientation_indicator.append(txt)
        self.group_orientation_indicator_with_pointer.append(self.group_orientation_indicator)
        self.group_orientation_indicator_with_pointer.attributes['transform'] = 'translate(0 %s)'%(max_radius+orientation_indicator_y_pos)

        self.orientation_pointer = gui.SvgPolygon(3)
        self.orientation_pointer.set_fill('red')
        self.orientation_pointer.set_stroke(1, 'black')
        self.orientation_pointer.add_coord(-0.04, -0.06)
        self.orientation_pointer.add_coord(0.0, 0.0)
        self.orientation_pointer.add_coord(0.04, -0.06)
        self.orientation_pointer.attributes['transform'] = 'translate(0 %s)'%(-max_radius)
        self.group_orientation_indicator_with_pointer.append(self.orientation_pointer)

        self.append(self.group_orientation_indicator_with_pointer)


    def generate_pitch_indicator(self):
        self.group_pitch_indicator.empty()
        s1 = 0.05 #min_sign_width
        s2 = 0.1 #mid_sign_width
        s3 = 0.20 #max_sign_width
        index = 0
        radius = 1.0
        step = 2.5
        angle_min = -90
        angle_max = 90
        sign_sizes = [s3,   s1, s2,   s1]
        for angle in range(int(angle_min*10), int(angle_max*10), int(step*10)):
            sign_size = sign_sizes[index%len(sign_sizes)]
            index += 1
            angle = angle/10.0
            #angle = math.degrees(math.acos(math.cos(math.radians(angle))))
            hide_scale = abs(angle) > self.pitch_roll_scale_limit
            
            if angle == 0:
                sign_size = 0
            y = -math.sin(math.radians(90.0))/90.0*(angle)*radius
            line = gui.SvgLine(-sign_size/2, y, sign_size/2, y)
            line.set_stroke(0.01, 'rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
            self.group_pitch_indicator.append(line)

            #if it is a big sign, add also text
            if sign_size == s3:
                txt = gui.SvgText(sign_size/2, y, str(int(angle)))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'start'
                txt.set_fill('rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
                txt.css_font_size = '0.04px'
                self.group_pitch_indicator.append(txt)

                txt = gui.SvgText(-sign_size/2, y, str(int(angle)))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'end'
                txt.set_fill('rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
                txt.css_font_size = '0.04px'
                self.group_pitch_indicator.append(txt)

    def set_pitch(self, pitch):
        self.pitch = pitch
        
    def set_orientation(self, orientation):
        self.orientation = orientation
        
    def set_roll(self, roll):
        self.roll = roll

    def update_attitude(self):
        #self.group_pitch.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.orientation, math.sin(math.radians(self.pitch)))
        
        self.group_roll.attributes['transform'] = "rotate(%s 0 0)"%(-self.roll)
        
        self.group_roll_indicator.attributes['transform'] = "rotate(%s 0 0)"%(-self.roll)
        self.group_roll_indicator.css_transform_origin = "0% 0%"
        
        offset = (math.sin(math.radians(90.0))/90.0*self.pitch*1.0)
        self.group_pitch.attributes['transform'] = "translate(0 %s)"%offset
        self.group_horizon_terrain.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(-self.roll, (offset*0.4))
        self.group_roll.css_transform_origin = "50%% %.2fpx"%(-offset+0.97)
        
        self.group_orientation_indicator.attributes['transform'] = "rotate(%s 0 0)"%(-self.orientation)

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
        vbox0 = gui.VBox(width="100%", height="100%")

        self.pfd = PrimaryFlightDisplay(width="100%", height="100%")
        vbox0.append(self.pfd)

        self.slider_pitch = gui.SpinBox(0, -90.0, 90.0, 2.0)
        self.slider_orientation = gui.SpinBox(0, -180, 180, 2)
        self.slider_roll = gui.SpinBox(0, -180, 180, 2.0)

        vbox0.append( gui.HBox(children=[gui.Label('pitch'), self.slider_pitch], width=300) )
        vbox0.append( gui.HBox(children=[gui.Label('orientation'), self.slider_orientation], width=300) )
        vbox0.append( gui.HBox(children=[gui.Label('roll'), self.slider_roll], width=300) )

        return vbox0
    


#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': True, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    start(Application, address='0.0.0.0', port=8081, multiple_instance=False, start_browser=True, debug=False)
