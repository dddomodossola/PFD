
# -*- coding: utf-8 -*-

from remi import gui
from remi import start, App
import math


class TapeVertical(gui.SvgGroup):
    value = 0
    scale_length = 1000
    scale_length_visible = 100

    subcontainer = None #contains the moving scale
    pointer_with_value_group = None #contains the static pointer with actual value

    wide = 0
    high = 0

    left_side = True

    def __init__(self, x_pos, y_pos, wide, high, left_side, *args, **kwargs):
        """ x_pos and y_pos are coordinates indicated by the pointer, generally at the center of the shown tape
        """
        gui.SvgGroup.__init__(self, *args, **kwargs)

        self.wide = wide
        self.high = high

        self.left_side = left_side
        
        self.attributes['transform'] = 'translate(%s %s)'%(x_pos, y_pos)

        #it is used a subcontainer in order to show only a part of the entire tape
        self.subcontainer = gui.SvgSubcontainer(-wide if self.left_side else 0, -self.high/2, wide, high)
        self.subcontainer.set_viewbox(-self.wide/2, -self.scale_length_visible/2, wide, self.scale_length_visible)
        self.append(self.subcontainer)

        #horizontal line along all the tape size
        self.group_indicator = gui.SvgGroup()
        x = self.wide/2 if self.left_side else -self.wide/2
        line = gui.SvgLine(x, 0, x, -self.scale_length)
        line.set_stroke(0.1*self.wide, 'white')
        self.group_indicator.append(line)
        
        #creating labels
        labels = {}
        labels_size = {}
        for i in range(0, self.scale_length+1, 10):
            if not i in labels.keys():
                labels[i] = "%d"%i 
                labels_size[i] = 1.0

        indicator_size = self.wide*0.2
        for v in range(0, int(self.scale_length)+1):
            if v in labels.keys():
                x =  (self.wide/2-indicator_size) if self.left_side else (-self.wide/2+indicator_size)
                y = -v
                line = gui.SvgLine(x, y, self.wide/2 if self.left_side else -self.wide/2, y)
                line.set_stroke(0.03*self.wide, 'white')
                self.group_indicator.append(line)

                txt = gui.SvgText(x, y, labels.get(v, ''))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'end' if self.left_side else 'start'
                txt.set_fill('white')
                txt.css_font_size = gui.to_pix(0.3*self.wide*labels_size[v])
                txt.css_font_weight = 'bolder'
                self.group_indicator.append(txt)
        self.subcontainer.append(self.group_indicator)
        #self.group_indicator.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        
        self.pointer = gui.SvgPolygon(3)
        self.pointer.set_fill('violet')
        self.pointer.set_stroke(0.005*self.scale_length_visible, 'black')
        self.pointer.add_coord(0.2*self.wide*(-1 if self.left_side else 1 ), 0)
        self.pointer.add_coord(0, 0.1*self.wide)
        self.pointer.add_coord(0, -0.1*self.wide)        
        #self.pointer.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(self.pointer)

        pointer_value = gui.SvgText(0, 0, "%d"%(self.value%360))
        pointer_value.attr_dominant_baseline = 'middle'
        pointer_value.attr_text_anchor = 'start' if self.left_side else 'end'
        pointer_value.set_fill('white')
        pointer_value.css_font_size = gui.to_pix(0.5*self.wide)
        pointer_value.css_font_weight = 'bolder'
        #pointer_value.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(pointer_value)
        
    def set_value(self, value):
        self.value = value
        self.subcontainer.set_viewbox(-self.wide/2, -self.scale_length_visible/2 - self.value, self.wide, self.scale_length_visible)


class OrientationTapeHorizontal(gui.SvgGroup):
    orientation = 0
    scale_length = 720
    scale_length_visible = 180

    subcontainer = None #contains the moving scale
    pointer_with_value_group = None #contains the static pointer with actual value

    wide = 0
    high = 0

    def __init__(self, x_pos, y_pos, wide, high, *args, **kwargs):
        """ x_pos and y_pos are coordinates indicated by the pointer, generally at the center of the shown tape
        """
        gui.SvgGroup.__init__(self, *args, **kwargs)

        self.wide = wide
        self.high = high
        
        self.attributes['transform'] = 'translate(%s %s)'%(x_pos, y_pos)

        #it is used a subcontainer in order to show only a part of the entire tape
        self.subcontainer = gui.SvgSubcontainer(-wide/2, 0, wide, high)
        self.subcontainer.set_viewbox(-self.scale_length_visible/2, 0, self.scale_length_visible, high)
        self.append(self.subcontainer)

        #horizontal line along all the tape size
        self.group_orientation_indicator = gui.SvgGroup()
        line = gui.SvgLine(-self.scale_length/2, 0, self.scale_length/2, 0)
        line.set_stroke(0.005*high, 'white')
        self.group_orientation_indicator.append(line)
        
        #creating labels
        labels = {0:'N', 90:'E', 180:'S', 270:'W'}
        labels_size = {0:1.0, 90:1.0, 180:1.0, 270:1.0}
        for i in range(0, 36+1, 2):
            if not (i*10) in labels.keys():
                labels[i*10] = "%02d"%i 
                labels_size[i*10] = 0.7

        for angle in range(int(-self.scale_length/2), int(self.scale_length/2)+1):
            if angle%360 in labels.keys():
                x =  angle
                y = 0.05*self.high * labels_size[angle%360]
                line = gui.SvgLine(x, 0, x, y)
                line.set_stroke(1, 'white')
                self.group_orientation_indicator.append(line)

                txt = gui.SvgText(x, y, labels.get(angle%360, ''))
                txt.attr_dominant_baseline = 'hanging'
                txt.attr_text_anchor = 'middle'
                txt.set_fill('white')
                txt.css_font_size = gui.to_pix(5*labels_size[angle%360])
                txt.css_font_weight = 'bolder'
                self.group_orientation_indicator.append(txt)
        self.subcontainer.append(self.group_orientation_indicator)
        #self.group_orientation_indicator.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        
        self.orientation_pointer = gui.SvgPolygon(3)
        self.orientation_pointer.set_fill('red')
        self.orientation_pointer.set_stroke(0.005*self.scale_length_visible, 'black')
        self.orientation_pointer.add_coord(-0.01*self.scale_length_visible, -0.02*self.high)
        self.orientation_pointer.add_coord(0.0*self.scale_length_visible, 0.0*self.high)
        self.orientation_pointer.add_coord(0.01*self.scale_length_visible, -0.02*self.high)        
        #self.orientation_pointer.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(self.orientation_pointer)

        orientation_value = gui.SvgText(0, -0.03*high, "%d"%(self.orientation%360))
        orientation_value.attr_dominant_baseline = 'auto'
        orientation_value.attr_text_anchor = 'middle'
        orientation_value.set_fill('white')
        orientation_value.css_font_size = gui.to_pix(0.03*self.scale_length_visible)
        orientation_value.css_font_weight = 'bolder'
        #orientation_value.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(orientation_value)
        
    def set_orientation(self, value):
        self.orientation = value
        self.subcontainer.set_viewbox(-self.scale_length_visible/2 + self.orientation, 0, self.scale_length_visible, self.high)


class AttitudeIndicator(gui.SvgSubcontainer):
    pitch = 0
    orientation = 0
    roll = 0

    pitch_roll_scale_limit = 60

    vw = 100
    vh = 100
    
    def __init__(self, *args, **kwargs):

        gui.SvgSubcontainer.__init__(self, -self.vw/2, -self.vh/2, self.vw, self.vh, *args, **kwargs)

        self.attr_viewBox = "%s %s %s %s"%(-self.vw/2, -self.vh/2, self.vw, self.vh)
        
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
        self.horizon_background = gui.SvgRectangle(-self.vw/2, -self.vh/2, self.vw, self.vh)
        self.horizon_background.set_fill("rgb(0,100,255)")
        self.append(self.horizon_background)

        self.group_horizon_terrain = gui.SvgGroup()
        self.horizon_terrain = gui.SvgRectangle(-self.vw, 0, self.vw*2, self.vh*2)
        self.horizon_terrain.set_fill("rgb(53, 151, 0)")
        self.horizon_terrain.set_stroke(self.vh/1000.0, "lightgray")
        self.group_horizon_terrain.append(self.horizon_terrain)
        self.append(self.group_horizon_terrain)

        #pitch angle indication
        self.group_pitch_indicator = gui.SvgGroup()
        self.group_pitch.append(self.group_pitch_indicator)
        self.generate_pitch_indicator()

        self.append(self.group_roll)


        #roll angle indication
        min_radius = self.vw*0.45
        mid_radius = self.vw*0.48
        max_radius = self.vw*0.5
        angle_min = -60
        angle_max = 60
        angle_step = 5
        for angle in range(angle_min, angle_max+angle_step, angle_step):
            r = min_radius if (angle%10)==0 else mid_radius
            x_min = math.cos(math.radians(angle+90))*r
            y_min = -math.sin(math.radians(angle+90))*r
            x_max = math.cos(math.radians(angle+90))*max_radius
            y_max = -math.sin(math.radians(angle+90))*max_radius
            
            hide_scale = abs(int(angle))>self.pitch_roll_scale_limit

            line = gui.SvgLine(x_min, y_min, x_max, y_max)
            line.set_stroke(self.vw*0.005, 'white' if not hide_scale else 'transparent')
            self.append(line)
            if (angle%10)==0:
                x_txt = math.cos(math.radians(angle+90))*(min_radius-0.025*self.vw)
                y_txt = -math.sin(math.radians(angle+90))*(min_radius-0.025*self.vw)
                txt = gui.SvgText(x_txt, y_txt, str(abs(int(angle))))
                txt.attr_dominant_baseline = 'hanging'
                txt.attr_text_anchor = 'middle'
                txt.set_fill('white' if not hide_scale else 'transparent')
                txt.css_font_size = gui.to_pix(self.vw*0.04)
                txt.css_font_weight = 'bolder'
                self.append(txt)


        self.group_roll_indicator = gui.SvgGroup()
        self.group_roll_indicator.css_visibility = 'visible'
        self.append(self.group_roll_indicator)

        #roll and bank indicator
        self.group_roll_and_bank_angle_indicator = gui.SvgGroup()
        self.roll_indicator = gui.SvgPolygon(3)
        self.roll_indicator.set_fill('red')
        self.roll_indicator.set_stroke(1, 'black')
        self.roll_indicator.add_coord(-0.04*self.vw, -0.06*self.vw)
        self.roll_indicator.add_coord(0.0*self.vw, (-0.06 - 0.03)*self.vw)
        self.roll_indicator.add_coord(0.04*self.vw, -0.06*self.vw)
        self.group_roll_and_bank_angle_indicator.append(self.roll_indicator)
        self.bank_indicator = gui.SvgPolygon(4)
        self.bank_indicator.set_fill('transparent')
        self.bank_indicator.set_stroke(1, 'black')
        self.bank_indicator.add_coord(-0.04*self.vw, (-0.06 + 0.005)*self.vw)
        self.bank_indicator.add_coord(0.04*self.vw, (-0.06 + 0.005)*self.vw)
        self.bank_indicator.add_coord(0.04*self.vw, (-0.06 + 0.025)*self.vw)
        self.bank_indicator.add_coord(-0.04*self.vw, (-0.06 + 0.025)*self.vw)
        self.group_roll_and_bank_angle_indicator.append(self.bank_indicator)
        self.group_roll_and_bank_angle_indicator.attributes['transform'] = "translate(0 %s)"%(-0.3*self.vh)
        self.group_roll_indicator.append(self.group_roll_and_bank_angle_indicator)

        #airplaine indicator is steady
        thick = 0.02*self.vw
        self.airplane_svg_left = gui.SvgPolygon(8)
        self.airplane_svg_left.set_fill('gray')
        self.airplane_svg_left.set_stroke(0.005*self.vw, 'black')
        self.airplane_svg_left.add_coord(-0.2*self.vw, 0*self.vw) #25x8
        self.airplane_svg_left.add_coord(-0.40*self.vw, 0*self.vw)
        self.airplane_svg_left.add_coord(-0.40*self.vw, thick)
        self.airplane_svg_left.add_coord(-0.2*self.vw - thick, thick)
        self.airplane_svg_left.add_coord(-0.2*self.vw - thick, thick + 0.08*self.vw)
        self.airplane_svg_left.add_coord(-0.2*self.vw, thick + 0.08*self.vw)
        self.airplane_svg_left.add_coord(-0.2*self.vw, 0.08*self.vw)

        self.airplane_svg_right = gui.SvgPolygon(8)
        self.airplane_svg_right.set_fill('gray')
        self.airplane_svg_right.set_stroke(0.005*self.vw, 'black')
        self.airplane_svg_right.add_coord(0.2*self.vw, 0*self.vw) #25x8
        self.airplane_svg_right.add_coord(0.40*self.vw, 0*self.vw)
        self.airplane_svg_right.add_coord(0.40*self.vw, thick)
        self.airplane_svg_right.add_coord(0.2*self.vw + thick, thick)
        self.airplane_svg_right.add_coord(0.2*self.vw + thick, thick + 0.08*self.vw)
        self.airplane_svg_right.add_coord(0.2*self.vw, thick + 0.08*self.vw)
        self.airplane_svg_right.add_coord(0.2*self.vw, 0.08*self.vw)

        self.airplane_svg_center = gui.SvgRectangle(-0.02*self.vw, -0.02*self.vw, 0.04*self.vw, 0.04*self.vw)
        self.airplane_svg_center.set_fill('white')
        self.airplane_svg_center.set_stroke(0.005*self.vw, 'lightgray')

        self.append([self.airplane_svg_left, self.airplane_svg_right, self.airplane_svg_center])

        #self.generate_orientation_indicator()
        self.orientation_tape = OrientationTapeHorizontal(0, 0.3*self.vh, 0.8*self.vw, 1*self.vh)
        self.append(self.orientation_tape)

    def generate_pitch_indicator(self):
        self.group_pitch_indicator.empty()
        s1 = 0.05*self.vw #min_sign_width
        s2 = 0.1*self.vw #mid_sign_width
        s3 = 0.20*self.vw #max_sign_width
        index = 0
        radius = 1.0*self.vw
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
            line.set_stroke(0.01*self.vw, 'rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
            self.group_pitch_indicator.append(line)

            #if it is a big sign, add also text
            if sign_size == s3:
                txt = gui.SvgText(sign_size/2, y, str(int(angle)))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'start'
                txt.set_fill('rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
                txt.css_font_size = gui.to_pix(0.04*self.vw)
                self.group_pitch_indicator.append(txt)

                txt = gui.SvgText(-sign_size/2, y, str(int(angle)))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'end'
                txt.set_fill('rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
                txt.css_font_size = gui.to_pix(0.04*self.vw)
                self.group_pitch_indicator.append(txt)

    def set_pitch(self, pitch):
        self.pitch = pitch
        
    def set_orientation(self, orientation):
        self.orientation = orientation
        
    def set_roll(self, roll):
        self.roll = roll

    def update_attitude(self):
        if self.group_roll_indicator.css_visibility == 'visible' and abs(self.roll) > 90:
            self.group_roll_indicator.css_visibility = 'hidden'
        if self.group_roll_indicator.css_visibility == 'hidden' and abs(self.roll) <= 90:
            self.group_roll_indicator.css_visibility = 'visible'

        #self.generate_orientation_indicator()
        #self.orientation_subcontainer.set_viewbox(-90 + self.orientation, 0, 180, 1*self.vh)
        self.orientation_tape.set_orientation(self.orientation)

        #self.group_pitch.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.orientation, math.sin(math.radians(self.pitch)))
        
        self.group_roll.attributes['transform'] = "rotate(%s 0 0)"%(-self.roll)
        
        self.group_roll_indicator.attributes['transform'] = "rotate(%s 0 0)"%(-self.roll)
        self.group_roll_indicator.css_transform_origin = "0% 0%"
        
        offset = (math.sin(math.radians(90.0))/90.0*self.pitch*self.vw)
        self.group_pitch.attributes['transform'] = "translate(0 %s)"%offset
        self.group_horizon_terrain.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(-self.roll, (offset*0.4))
        self.group_roll.css_transform_origin = "50%% %.2fpx"%(-offset+0.97*self.vw)
        
        #self.group_orientation_indicator.attributes['transform'] = "rotate(%s 0 0)"%(-self.orientation)

class PrimaryFlightDisplay(gui.Svg):
    def __init__(self, *args, **kwargs):
        gui.Svg.__init__(self, *args, **kwargs)
        self.attr_viewBox = "-100 -50 200 100"
        background = gui.SvgRectangle(-100, -50, 200, 100)
        background.set_fill('black')
        self.append(background)

        self.attitude_indicator = AttitudeIndicator()
        self.append(self.attitude_indicator)

        self.left_tape = TapeVertical(-80, 0, 10, 80, True)
        self.append(self.left_tape)

        self.right_tape = TapeVertical(80, 0, 10, 80, False)
        self.append(self.right_tape)

    def set_attitude_pitch(self, value):
        self.attitude_indicator.set_pitch(value)

    def set_attitude_orientation(self, value):
        self.attitude_indicator.set_orientation(value)
        self.left_tape.set_value(value)

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
    

if __name__ == "__main__":
    start(Application, address='0.0.0.0', port=8080, multiple_instance=False, start_browser=True, debug=False)
