
# -*- coding: utf-8 -*-

from remi import gui
from remi import start, App
import math
import threading
import time
import base64
import pyvips
import io

class AsciiContainer(gui.Container):
    widget_layout_map = None

    def __init__(self, *args, **kwargs):
        gui.Container.__init__(self, *args, **kwargs)
        self.css_position = 'relative'
        
    def set_from_asciiart(self, asciipattern, gap_horizontal=0, gap_vertical=0):
        """
            asciipattern (str): a multiline string representing the layout
                | widget1               |
                | widget1               |
                | widget2 | widget3     |
            gap_horizontal (int): a percent value
            gap_vertical (int): a percent value
        """
        pattern_rows = asciipattern.split('\n')
        # remove empty rows
        for r in pattern_rows[:]:
            if len(r.replace(" ", "")) < 1:
                pattern_rows.remove(r)

        layout_height_in_chars = len(pattern_rows)
        self.widget_layout_map = {}
        row_index = 0
        for row in pattern_rows:
            row = row.strip()
            row_width = len(row) - row.count('|') #the row width is calculated without pipes
            row = row[1:-1] #removing |pipes at beginning and end
            columns = row.split('|')

            left_value = 0
            for column in columns:
                widget_key = column.strip()
                widget_width = float(len(column))
                
                if not widget_key in self.widget_layout_map.keys():
                    #width is calculated in percent
                    # height is instead initialized at 1 and incremented by 1 each row the key is present
                    # at the end of algorithm the height will be converted in percent
                    self.widget_layout_map[widget_key] = { 'width': float(widget_width / (row_width) * 100.0 - gap_horizontal), 
                                            'height':1, 
                                            'top':float(row_index / (layout_height_in_chars) * 100.0 + (gap_vertical/2.0)), 
                                            'left':float(left_value / (row_width) * 100.0 + (gap_horizontal/2.0))}
                else:
                    self.widget_layout_map[widget_key]['height'] += 1
                
                left_value += widget_width
            row_index += 1

        #converting height values in percent string
        for key in self.widget_layout_map.keys():
            self.widget_layout_map[key]['height'] = float(self.widget_layout_map[key]['height'] / (layout_height_in_chars) * 100.0 - gap_vertical) 

        for key in self.widget_layout_map.keys():
            self.set_widget_layout(key)

    def append(self, widget, key=''):
        key = gui.Container.append(self, widget, key)
        self.set_widget_layout(key)
        return key

    def set_widget_layout(self, widget_key):
        if not ((widget_key in self.children.keys() and (widget_key in self.widget_layout_map.keys()))):
            return
        self.children[widget_key].css_position = 'absolute'
        self.children[widget_key].set_size("%.2f%%"%self.widget_layout_map[widget_key]['width'], "%.2f%%"%self.widget_layout_map[widget_key]['height'])
        self.children[widget_key].css_left = "%.2f%%"%self.widget_layout_map[widget_key]['left']
        self.children[widget_key].css_top = "%.2f%%"%self.widget_layout_map[widget_key]['top']


class SimpleVSI(gui.SvgGroup):
    value = 0

    def __init__(self, x_pos, y_pos, wide, high, *args, **kwargs):
        """ x_pos and y_pos are coordinates indicated by the pointer, generally at the center of the shown tape
        """
        gui.SvgGroup.__init__(self, *args, **kwargs)

        self.wide = wide
        self.high = high

        self.attributes['transform'] = 'translate(%s %s)'%(x_pos, y_pos)

        #it is used a subcontainer in order to show only a part of the entire tape
        self.subcontainer = gui.SvgSubcontainer(-self.wide, -self.high/2, wide, high)
        self.subcontainer.set_viewbox(-self.wide/2, -self.high/2, wide, self.high)
        self.append(self.subcontainer)

        vertical_line_width = self.wide/20
        scale_vertical_line = gui.SvgLine(-self.wide/2, -self.high/2, -self.wide/2, self.high)
        scale_vertical_line.set_stroke(vertical_line_width, 'lightgray')
        self.subcontainer.append(scale_vertical_line)

        self.pointer_line = gui.SvgLine(self.wide/2, 0, -self.wide/2, self.value*(self.high/2))
        self.pointer_line.set_stroke(self.wide/14, 'lightgray')
        self.subcontainer.append(self.pointer_line)

        self.value_max = gui.SvgText(-self.wide/2 + vertical_line_width, -self.high/2, "10")
        self.value_max.attr_dominant_baseline = 'hanging'
        self.value_max.attr_text_anchor = 'start'
        self.value_max.set_fill('white')
        self.value_max.css_font_size = gui.to_pix(0.3*self.wide)
        self.value_max.css_font_weight = 'bolder'
        #self.value_max.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.subcontainer.append(self.value_max)

        self.value_min = gui.SvgText(-self.wide/2 + vertical_line_width, self.high/2, "-10")
        self.value_min.attr_dominant_baseline = 'ideographic'
        self.value_min.attr_text_anchor = 'start'
        self.value_min.set_fill('white')
        self.value_min.css_font_size = gui.to_pix(0.3*self.wide)
        self.value_min.css_font_weight = 'bolder'
        #self.value_min.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.subcontainer.append(self.value_min)

    def set_value(self, value):
        self.value = value
        self.pointer_line.set_coords(self.wide/2, 0, -self.wide/2, -self.value*(self.high/2)/10)
        

class TapeVertical(gui.SvgGroup):
    value = 0
    scale_length = 1000
    scale_length_visible = 100

    subcontainer = None #contains the moving scale
    pointer_with_value_group = None #contains the static pointer with actual value

    wide = 0
    high = 0

    left_side = True

    indicator_size = 0

    tape_white_min = 0
    tape_white_max = 0

    tape_green_min = 0
    tape_green_max = 0


    def __init__(self, x_pos, y_pos, wide, high, left_side, scale_length, scale_length_visible, tape_white_min=0, tape_white_max=0, tape_green_min=0, tape_green_max=0, *args, **kwargs):
        """ x_pos and y_pos are coordinates indicated by the pointer, generally at the center of the shown tape
        """
        gui.SvgGroup.__init__(self, *args, **kwargs)

        self.scale_length = scale_length
        self.scale_length_visible = scale_length_visible

        self.wide = wide
        self.high = high

        self.indicator_size = self.wide*0.2
        self.left_side = left_side

        self.tape_white_min = tape_white_min 
        self.tape_white_max = tape_white_max

        self.tape_green_min = tape_green_min
        self.tape_green_max = tape_green_max
        
        self.attributes['transform'] = 'translate(%s %s)'%(x_pos, y_pos)

        #it is used a subcontainer in order to show only a part of the entire tape
        self.subcontainer = gui.SvgSubcontainer(-wide if self.left_side else 0, -self.high/2, wide, high)
        self.subcontainer.set_viewbox(-self.wide/2, -self.scale_length_visible/2, wide, self.scale_length_visible)
        self.append(self.subcontainer)

        self.group_indicator = gui.SvgGroup()
       
        self.group_scale = gui.SvgGroup()
        self.build_scale()

        self.group_indicator.append(self.group_scale)        

        self.subcontainer.append(self.group_indicator)

        
        #self.group_indicator.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        
        self.pointer = gui.SvgPolygon(5)
        self.pointer.set_fill('black')
        self.pointer.set_stroke(0.02*self.scale_length_visible, 'red')
        direction = (-1 if self.left_side else 1)
        pointer_x = 0 #(-self.wide if self.left_side else 0)
        pointer_width = self.wide
        self.pointer.add_coord(pointer_x, 0)
        self.pointer.add_coord(pointer_x+((0.2*self.wide)*direction), 0.2*self.wide)
        self.pointer.add_coord(pointer_x+pointer_width*direction, 0.2*self.wide)
        self.pointer.add_coord(pointer_x+pointer_width*direction, -0.2*self.wide)
        self.pointer.add_coord(pointer_x+((0.2*self.wide)*direction), -0.2*self.wide)
        #self.pointer.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(self.pointer)

        self.pointer_value = gui.SvgText(((0-self.indicator_size) if self.left_side else (self.wide-0.05*self.wide)), 0.3*self.wide/5*2, "%d"%(self.value%360))
        self.pointer_value.attr_dominant_baseline = 'middle'
        self.pointer_value.attr_text_anchor = 'end' if self.left_side else 'end'
        self.pointer_value.set_fill('lime')
        self.pointer_value.css_font_size = gui.to_pix(0.3*self.wide)
        self.pointer_value.css_font_weight = 'bolder'
        #self.pointer_value.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(self.pointer_value)

        if self.tape_green_max > 0:
            green_and_red_tape_width = self.wide
            white_tape_width = 3
            tape_green = gui.SvgRectangle(-self.wide/2, -self.tape_green_max, green_and_red_tape_width, (self.tape_green_max-self.tape_green_min))
            tape_green.set_fill('green')
            self.group_scale.add_child('tape_green', tape_green)
        if self.tape_white_max > 0:
            tape_white = gui.SvgRectangle((self.wide/2-white_tape_width if self.left_side else -self.wide/2), -self.tape_white_max, white_tape_width, (self.tape_white_max-self.tape_white_min))
            tape_white.set_fill('white')
            self.group_scale.add_child('tape_white', tape_white)
        if self.tape_green_max > 0:
            tape_red = gui.SvgRectangle(-self.wide/2, -self.scale_length, green_and_red_tape_width, (self.scale_length-self.tape_green_max))
            tape_red.set_fill('red')
            self.group_scale.add_child('tape_red', tape_red)

    def build_scale(self):
        #self.group_scale.empty()

        #horizontal line along all the tape size
        x = self.wide/2 if self.left_side else -self.wide/2
        line = gui.SvgLine(x, -self.value-self.scale_length_visible/2, x, -self.value+self.scale_length_visible/2)
        line.set_stroke(0.1*self.wide, 'gray')
        self.group_scale.append(line, "line")

        #creating labels
        labels = {}
        labels_size = {}
        step = 10
        for i in range(int(self.value/step -1 -(self.scale_length_visible/step)/2), int(self.value/step + (self.scale_length_visible/step)/2+1)):
            if not i*step in labels.keys() and i*step>=0:
                labels[i*step] = "%d"%(i*step) 
                labels_size[i*step] = 1.0

        indicator_x =  (self.wide/2-self.indicator_size) if self.left_side else (-self.wide/2+self.indicator_size)
        text_x = ((self.wide/2-self.indicator_size) if self.left_side else (self.wide/2-0.05*self.wide))
        font_size = 0.28*self.wide
        content = ""
        for v in range(int(self.value-self.scale_length_visible/2), int(self.value+self.scale_length_visible/2 +1)):
            if v in labels.keys():
                y = -v
                """line = gui.SvgLine(indicator_x, y, self.wide/2 if self.left_side else -self.wide/2, y)
                line.set_stroke(0.03*self.wide, 'gray')
                self.group_scale.append(line)
                """
                content += """<line class="SvgLine" x1="%(x1)s" y1="%(y1)s" x2="%(x2)s" y2="%(y2)s" stroke="gray" stroke-width="0.6"></line>"""%{'x1':indicator_x, 'y1':y, 'x2':(self.wide/2 if self.left_side else -self.wide/2), 'y2':y}

                content += """<text class="SvgText" x="%(x)s" y="%(y)s" fill="white" style="dominant-baseline:middle;text-anchor:end;font-size:%(font)s;font-weight:bolder">%(text)s</text>"""%{'x':text_x, 'y':y+font_size/5.0*2.0, 'text':labels.get(v, ''), 'font':gui.to_pix(font_size) }
                """txt = gui.SvgText(text_x, y, labels.get(v, ''))
                txt.attr_dominant_baseline = 'middle'
                txt.attr_text_anchor = 'end' if self.left_side else 'end'
                txt.set_fill('white')
                txt.css_font_size = gui.to_pix(0.25*self.wide*labels_size[v])
                txt.css_font_weight = 'bolder'
                self.group_scale.append(txt)"""
        self.group_scale.add_child('content', content)
                
    def set_value(self, value):
        self.value = value
        self.pointer_value.set_text("%d"%self.value)
        self.subcontainer.set_viewbox(-self.wide/2, -self.scale_length_visible/2 - self.value, self.wide, self.scale_length_visible)
        self.build_scale()


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
        self.subcontainer.set_viewbox(-self.scale_length_visible/2, 0, self.scale_length_visible, high*(high/wide))
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

                font_size = 7*labels_size[angle%360]
                txt = gui.SvgText(x, y + font_size, labels.get(angle%360, ''))
                txt.attr_dominant_baseline = 'hanging'
                txt.attr_text_anchor = 'middle'
                txt.set_fill('white')
                txt.css_font_size = gui.to_pix(font_size)
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

        self.orientation_value = gui.SvgText(0, -0.03*high, "%d"%(self.orientation%360))
        self.orientation_value.attr_dominant_baseline = 'auto'
        self.orientation_value.attr_text_anchor = 'middle'
        self.orientation_value.set_fill('white')
        self.orientation_value.css_font_size = gui.to_pix(0.03*self.scale_length_visible)
        self.orientation_value.css_font_weight = 'bolder'
        #orientation_value.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(self.orientation_value)
        
    def set_orientation(self, value):
        self.orientation = value
        self.orientation_value.set_text("%d"%(self.orientation%360))
        self.subcontainer.set_viewbox(-self.scale_length_visible/2 + self.orientation, 0, self.scale_length_visible, self.high*(self.high/self.wide))


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
        angle_step = 20  #was 5
        font_size = self.vw*0.04
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
                x_txt = math.cos(math.radians(angle+90))*(min_radius-0.025*self.vw-font_size/5*4)
                y_txt = -math.sin(math.radians(angle+90))*(min_radius-0.025*self.vw-font_size/5*4)
                txt = gui.SvgText(x_txt, y_txt, str(abs(int(angle))))
                txt.attr_dominant_baseline = 'hanging'
                txt.attr_text_anchor = 'middle'
                txt.set_fill('white' if not hide_scale else 'transparent')
                txt.css_font_size = gui.to_pix(font_size)
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
        self.group_roll_and_bank_angle_indicator.attributes['transform'] = "translate(0 %s)"%(-0.27*self.vh)
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
        self.orientation_tape = OrientationTapeHorizontal(0, 0.4*self.vh, 0.8*self.vw, 1.0*self.vh)
        self.append(self.orientation_tape)

    def generate_pitch_indicator(self):
        self.group_pitch_indicator.empty()
        s1 = 0.05*self.vw #min_sign_width
        s2 = 0.1*self.vw #mid_sign_width
        s3 = 0.20*self.vw #max_sign_width
        index = 0
        radius = 1.0*self.vw
        step = 5 # was 2.5
        angle_min = -90
        angle_max = 90
        sign_sizes =  [s3, s2]  # was sign_sizes = [s3,   s1, s2,   s1]
        font_size = 4.0
        content = ""
        for angle in range(int(angle_min*10), int(angle_max*10), int(step*10)):
            sign_size = sign_sizes[index%len(sign_sizes)]
            index += 1
            angle = angle/10.0
            #angle = math.degrees(math.acos(math.cos(math.radians(angle))))
            hide_scale = abs(angle) > self.pitch_roll_scale_limit
            
            if angle == 0:
                sign_size = 0
            y = -math.sin(math.radians(90.0))/90.0*(angle)*radius
            """
            line = gui.SvgLine(-sign_size/2, y, sign_size/2, y)
            line.set_stroke(0.01*self.vw, 'rgba(255,255,255,0.5)' if not hide_scale else 'transparent')
            self.group_pitch_indicator.append(line)
            """
            content += """<line class="SvgLine" x1="%(x1)s" y1="%(y1)s" x2="%(x2)s" y2="%(y2)s" stroke="rgba(255,255,255,0.5)" stroke-width="1.0"></line>"""%{'x1':-sign_size/2, 'y1':y, 'x2':sign_size/2, 'y2':y}

            #if it is a big sign, add also text
            if sign_size == s3:

                content += """<text class="SvgText" x="%(x)s" y="%(y)s" fill="rgba(255,255,255,0.5)" style="text-anchor:start;font-size:4.0px">%(text)s</text>"""%{'x':sign_size/2, 'y':y+font_size/5.0*2.0, 'text':str(int(angle))}
                content += """<text class="SvgText" x="%(x)s" y="%(y)s" fill="rgba(255,255,255,0.5)" style="text-anchor:end;font-size:4.0px">%(text)s</text>"""%{'x':-sign_size/2, 'y':y+font_size/5.0*2.0, 'text':str(int(angle))}
                """
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
                """
        self.group_pitch_indicator.add_child('content', content)

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
        self.attr_viewBox = "-72 -50 144 100"

        self.style['font-family'] = "Sans" #'Consolas'

        background = gui.SvgRectangle(-90, -50, 180, 100)
        background.set_fill('black')
        self.append(background)

        self.attitude_indicator = AttitudeIndicator()
        self.append(self.attitude_indicator)

        self.speed_indicator = TapeVertical(-50, 0, 20, 80, True, 999, 100, 12, 40, 25, 68) #three digits values
        self.append(self.speed_indicator)

        self.altitude_indicator = TapeVertical(50, 0, 20, 80, False, 9999, 100) #four digits values
        self.append(self.altitude_indicator)

        #x_pos, y_pos, wide, high, left_side, scale_length, scale_length_visible
        self.VSI_indicator = SimpleVSI(81, 0, 10, 50)
        self.append(self.VSI_indicator)

    def set_attitude_pitch(self, value):
        self.attitude_indicator.set_pitch(value)

    def set_attitude_orientation(self, value):
        self.attitude_indicator.set_orientation(value)

    def set_attitude_roll(self, value):
        self.attitude_indicator.set_roll(value)

    def set_altitude(self, value):
        self.altitude_indicator.set_value(value)

    def set_speed(self, value):
        self.speed_indicator.set_value(value)

    def set_VSI(self, value):
        self.VSI_indicator.set_value(value)

    def update_attitude(self):
        self.attitude_indicator.update_attitude()

    def set_image_size(self, w, h):
        #these two parameters are required by pyvips to size the image correctly
        self.attributes['width'] = str(w)
        self.attributes['height'] = str(h)

    def download(self, update_index=0):
        self.attributes['xmlns']="http://www.w3.org/2000/svg"
        content = gui.Widget.repr(self, None)
        
        #headers = {'Content-type': 'image/svg+xml'}
        headers = {'Content-type': 'image/png'}
        x = pyvips.Image.svgload_buffer(content.encode('utf8'))
        buf = x.write_to_buffer('.png')
        #buf.seek(0)

        #content = bb.read()

        return [buf, headers]


class Settings(gui.VBox):
    check_example_setting = None
    text_area_example_setting = None
    dropdown_example_setting = None

    def __init__(self, *args, **kwargs):
        gui.VBox.__init__(self, *args, **kwargs)
        self.css_justify_content='flex-start'
        self.check_example_setting = gui.CheckBoxLabel("a checkbox", style={'background-color':'transparent', 'color':'white'})

        self.text_area_example_setting = gui.TextInput(style={'background-color':'transparent', 'color':'white'})

        self.dropdown_example_setting = gui.DropDown(style={'background-color':'transparent', 'color':'white'})
        self.dropdown_example_setting.append(gui.DropDownItem("red"))
        self.dropdown_example_setting.append(gui.DropDownItem("yellow"))
        self.dropdown_example_setting.set_value("red")

        self.append_setting("CHECKBOX", self.check_example_setting)
        self.append_setting("TEXTAREA", self.text_area_example_setting)
        self.append_setting("ALARM COLOR DROPDOWN", self.dropdown_example_setting)

    def append_setting(self, label, widget):
        self.append( gui.HBox(children=[gui.Label(label, style={'margin-right':'10px'}), widget], style={'background-color':'transparent', 'color':'white'}) )

    def toggle_visibility(self):
        if self.css_display == 'none':
            self.css_display = 'flex'
        else:
            self.css_display = 'none'


class Application(App):
    color_flipper = None
    standard_label_color = 'white'
    thread_alive_flag = False
    INOP_condition = False
    INOP_sim = False
    INOP_telemetry_seen = False
    INOP_alarm_time = time.time()  # the time of alarm start
    INOP_alarm_limit = 30  # stop blinking after this many seconds
    INOP_last_telemetry = time.time() - 10
    ab = 0.1
    voltage_alarm = False
    rpm = 0
    rpm_alarm = False
    rpm_alarm_time = time.time()  # the time of alarm start
    rpm_alarm_limit = 30  # stop blinking after this many seconds
    rpm_active = False
    fix_alarm = False
    vibration_alarm = False
    mode_alarm = False
    mode_change_time = time.time()
    text_severity = 6  # 6=low severity  0=highest
    text_alarm_sec = 2  # how long to flash
    text_alarm_time = time.time()  # time when alarm started

    def idle(self):
        #idle function called every update cycle
        #self.svg_group.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.rotation, self.movement)

        self.pfd_container.style['background-image'] = "url('data:image/png;base64,%s')"%str(base64.b64encode(self.pfd.download()[0]))[2:-1]

        alarm_color = self.settings_panel.dropdown_example_setting.get_value() #'red'

        # Voltage alarm
        if self.voltage_alarm:
            self.t5.css_color = self.color_flipper[0]
            self.t5.css_background_color = alarm_color
        else:
            self.t5.css_color = self.standard_label_color
            del self.t5.css_background_color

        # RPM alarm
        if self.rpm_active and self.rpm < 500:  # low RPM / not running
            self.rpm_alarm = True
            self.rpm_alarm_time = time.time()
            self.rpm_active = False
        if not self.rpm_active and self.rpm > 500:
            self.rpm_active = True
            self.rpm_alarm = False
        if self.rpm_alarm and time.time() - self.rpm_alarm_time > self.rpm_alarm_limit:
            self.rpm_active = False
            self.rpm_alarm = False

        if self.rpm_alarm:
            self.t6.css_color = self.color_flipper[0]
            self.t6.css_background_color = alarm_color
        else:
            self.t6.css_color = self.standard_label_color
            del self.t6.css_background_color
        # GNSS Fix alarm
        if self.fix_alarm:
            self.s.css_color = self.color_flipper[0]
            self.s.css_background_color = alarm_color
        else:
            self.s.css_color = self.standard_label_color
            del self.s.css_background_color
        # Mode change awareness
        if time.time() - self.mode_change_time < 2:
            self.m.css_color = self.color_flipper[0]
            self.m.css_background_color = 'green'
        else:
            self.m.css_color = self.standard_label_color
            del self.m.css_background_color
        # Vibration alarm
        if self.vibration_alarm:
            self.left3.css_color = self.color_flipper[0]
            self.left3.css_background_color = alarm_color
            self.play_beep()
        else:
            self.left3.css_color = self.standard_label_color
            del self.left3.css_background_color

        # Display using text severity
        if self.text_severity < 6 and time.time() - self.text_alarm_time > self.text_alarm_sec:
            self.t1.css_background_color = 'green'
            if self.text_severity < 4:
                self.t1.css_color = self.color_flipper[0]
                self.t1.css_background_color = alarm_color
        else:
            self.t1.css_color = self.standard_label_color
            del self.t1.css_background_color

        # Notify of telemetry loss
        if time.time() - self.INOP_last_telemetry < 2:
            self.INOP_condition = False
            self.INOP_telemetry_seen = True
        else:
            if self.INOP_telemetry_seen: self.INOP_condition = True

        if self.INOP_condition and time.time() - self.INOP_last_telemetry > self.INOP_alarm_limit:
            self.INOP_condition = False
            self.INOP_telemetry_seen = False

        if self.INOP_condition or self.INOP_sim:
            self.centering_container.css_background_color = {'red': 'black', 'black': 'red'}[
                self.centering_container.css_background_color]
        else:
            self.centering_container.css_background_color = 'black'

        #swap colors each update
        self.color_flipper = [self.color_flipper[1],self.color_flipper[0]]
        
    def play_beep(self):
        """to avoid playing audio repeatedly in a short time, I handle a timeout"""
        if time.time() - self.beep_timeout > 3: #the beep will be played with a minimum interval of 3 seconds
            self.execute_javascript('document.getElementById("audio").play();')
            self.beep_timeout = time.time()

    def main(self):
        self.color_flipper = ['orange', 'white']

        self.beep_timeout = time.time()
        data = gui.load_resource('./sound.wav')
        
        self.centering_container = gui.Container(width=640, height=360, style={'background-color':'black', "position":"absolute", 'overflow':'show'})
        self.centering_container.add_child("audio", """<audio id="audio" style="visibility:hidden;height:0px;width:0px;position:absolute" controls><source src="%s" /></audio>"""%data)

        self.settings_panel = Settings(width="100%", height=360, style={'background-color':'black'})
        self.settings_panel.toggle_visibility()

        #to make a left margin or 50px (because of google glasses curvature), I have to calculate a new height
        _w_margin  = 40
        _h_margin = 0  # was _w_margin*360/640

        self.main_container = AsciiContainer(width=640-_w_margin, height=360-_h_margin, style={'background-color':'transparent', 'position':'relative', 'margin-left':gui.to_pix(_w_margin), 'margin-top':gui.to_pix(_h_margin/2)})

        self.main_container.set_from_asciiart("""
        | t0                                                                                                     |
        | left1                | pfd                                                                             |
        | left1                | pfd                                                                             |
        | left1                | pfd                                                                             |
        | left2                | pfd                                                                             |
        | left2                | pfd                                                                             |
        | left2                | pfd                                                                             |
        | left3                | pfd                                                                             |
        | left3                | pfd                                                                             |
        | left3                | pfd                                                                             |
        | left4                | pfd                                                                             |
        | left4                | pfd                                                                             |
        | left4                | pfd                                                                             |
        | s            | m                                   | t5                                 | t6           |
        | t1                                                                                                     |
        """, gap_horizontal=0, gap_vertical=0)
        

        w = "95%"
        h = 30
        self.slider_pitch = gui.SpinBox(0, -90.0, 90.0, 2.0, width=w, height=h)
        self.slider_orientation = gui.SpinBox(0, -180, 180, 2, width=w, height=h)
        self.slider_roll = gui.SpinBox(0, -180, 180, 2.0, width=w, height=h)
        self.slider_altitude = gui.SpinBox(0, 0, 9999, 1.0, width=w, height=h)
        self.slider_speed = gui.SpinBox(0, 0, 999, 1.0, width=w, height=h)
        """
        controls_container = gui.VBox()
        controls_container.append( gui.VBox(children=[gui.Label('pitch'), self.slider_pitch], width=300) )
        controls_container.append( gui.VBox(children=[gui.Label('orientation'), self.slider_orientation], width=300) )
        controls_container.append( gui.VBox(children=[gui.Label('roll'), self.slider_roll], width=300) )
        controls_container.append( gui.VBox(children=[gui.Label('altitude'), self.slider_altitude], width=300) )
        controls_container.append( gui.VBox(children=[gui.Label('speed'), self.slider_speed], width=300) )

        hbox0.append(controls_container)
        """
        h_divisions = 14.0
        self.pfd = PrimaryFlightDisplay(style={'position':'relative'})
        self.pfd.set_image_size((640.0-_w_margin)*self.main_container.widget_layout_map["pfd"]['width']/100.0, (360.0 - _h_margin)*self.main_container.widget_layout_map["pfd"]['height']/100.0)
        
        _style = {'text-align':'center', 'color':self.standard_label_color, 'outline':'1px solid black', 'font-size':'16px'}
        self.t0 =       gui.Label("T0",     style=_style)
        self.t1 = gui.Label("WAITING FOR MAVLINK", style=_style)
        self.t5 = gui.Label("Voltage", style=_style)
        self.t6 = gui.Label("RPM", style=_style)
        self.s = gui.Label("GNSS", style=_style)
        self.m = gui.Label("MODE", style=_style)
        self.left1 = gui.Label("", style=_style)
        self.left2 = gui.Label("", style=_style)
        self.left3 = gui.Label("", style=_style)
        self.left4 = gui.Label("", style=_style)

        self.pfd_container = gui.Widget(style={'position':'relative', 'background-repeat':'no-repeat', 'background-color':'black', 'background-size':'contain'})
        self.main_container.append(self.pfd_container, "pfd")
        self.main_container.append(self.t0, "t0")
        self.main_container.append(self.t1, "t1")
        self.main_container.append(self.t5, "t5")
        self.main_container.append(self.t6, "t6")
        self.main_container.append(self.s, "s")
        self.main_container.append(self.m, "m")
        self.main_container.append(self.left1, "left1")
        self.main_container.append(self.left2, "left2")
        self.main_container.append(self.left3, "left3")
        self.main_container.append(self.left4, "left4")
    
        self.t1.onclick.do(self.on_t1_clicked)

        # Here I start a parallel thread
        self.thread_alive_flag = True
        t = threading.Thread(target=self.my_threaded_function)
        t.start()

        self.centering_container.append(self.main_container)
        self.centering_container.append(self.settings_panel)
        return self.centering_container

    def on_t1_clicked(self, emitter):
        self.play_beep()
        self.settings_panel.toggle_visibility()

    def my_threaded_function(self):
        testmsg = [[6, "Mission: 1 WP"],
                   [4, "Throttle failsafe on"],
                   [4, "Failsafe. Short event on: type=1/reason=3"],
                   [4, "Failsafe. Long event on: type=2/reason=3"],
                   [1, "123456789012345678901234567890123456789012345678901234567890ABCDEFGH"],
                   [4, "Failsafe. Long event off: reason=3"],
                   [6, "ArduPlane V4.0.6 (036ad450)"],
                   [6, "ChibiOS: d4fce84e"],
                   [6, "CubeBlack 003D0043 32385108 32373737"],
                   [6, "Throttle disarmed"],
                   [6, "RCOut: PWM:1-12"],
                   [6, "Ground start"],
                   [1, "Beginning INS calibration. Do not move plane"],
                   [6, "Calibrating barometer"],
                   [6, "Barometer 1 calibration complete"],
                   [6, "Barometer 2 calibration complete"],
                   [6, "Airspeed calibration started"],
                   [6, "Ground start complete"],
                   [2, "PreArm: radio Failsafe On"],
                   [4, "Throttle failsafe off"],
                   [6, "GPS 1: detected as u-blox at 115200 baud"],
                   [6, "EKF2 IMU0 initial yaw alignment complete"],
                   [6, "EKF2 IMU1 initial yaw alignment complete"],
                   [6, "Airspeed 1 calibrated"],
                   [6, "EKF2 IMU1 tilt alignment complete"],
                   [6, "EKF2 IMU0 tilt alignment complete"],
                   [6, "EKF2 IMU0 origin set"],
                   [6, "EKF2 IMU1 origin set"],
                   [6, "GPS: u-blox 1 saving config"],
                   [6, "u-blox 1 HW: 00080000 SW: EXT CORE 3.01 (d080e3)"],
                   [6, "EKF2 IMU0 is using GPS"],
                   [6, "EKF2 IMU1 is using GPS"],
                   [6, "Throttle armed"],
                   [6, "Flight plan received"],
                   [2, "EKF Variance"],
                   [4, "GPS Glitch"],
                   [4, "GPS Glitch cleared"],
                   [6, "Mission: 1 WP"],
                   [6, "EKF2 IMU0 switching to compass 1"],
                   [6, "EKF2 IMU1 switching to compass 1"],
                   [6, "Reached waypoint #1 dist 29m"],
                   [6, "Mission: 2 WP"],
                   [6, "Reached waypoint #2 dist 30m"],
                   [6, "Mission: 3 WP"]]

        mode_array_test = ["MANUAL", "CIRCLE", "STABILIZE", "TRAINING", "ACRO", "FLY_BY_WIRE_A", "FLY_BY_WIRE_B",
                           "CRUISE", "AUTOTUNE", "AUTO", "RTL", "LOITER", "TAKEOFF", "AVOID_ADSB", "GUIDED",
                           "INITIALISING", "QSTABILIZE", "QHOVER", "QLOITER", "QLAND", "QRTL", "QAUTOTUNE", "QACRO"]

        incrementa_number_for_testing = 0
        t1_text = ""
        t1_ptr = 0
        m_ptr = 0
        yaw = 0
        m = 0
        mode_last = -1
        time_for_text = time.time()
        time_for_mode = time.time()

        while self.thread_alive_flag:
            #calculations
            yaw = yaw - 3
            if yaw < 0:
                yaw = 360
            self.ab +=0.5
            if self.ab > 70: self.ab=-70

            # text simulation
            # horizontal space for max 68 chars with 16 px font
            if time.time() - time_for_text > 3:  # time to change text

                time_for_text = time.time()
                # fetch new message
                t1_text = testmsg[t1_ptr][1]
                self.text_severity = testmsg[t1_ptr][0]
                t1_ptr += 1
                if t1_ptr == len(testmsg):
                    t1_ptr = 0

            # mode simulation
            if time.time() - time_for_mode > 10:  # time to change text
                time_for_mode = time.time()
                # fetch new message
                m = mode_array_test[m_ptr]
                if mode_last != m_ptr:
                    mode_last = m_ptr
                    self.mode_change_time = time.time()

                m_ptr += 1
                if m_ptr == len(mode_array_test):
                    m_ptr = 0

            pitch=self.ab
            roll=self.ab
            alt=abs(self.ab*1.5+400)
            speed=abs(self.ab)

            # trigger some test alarms
            if alt > 290 and alt < 310:
                self.voltage_alarm = True
            else:
                self.voltage_alarm = False

            if alt > 320 and alt < 340:
                self.mode_alarm = True
            else:
                self.mode_alarm = False

            if alt > 360 and alt < 380:
                self.rpm_alarm = True
                self.INOP_sim = True
            else:
                self.rpm_alarm = False
                self.INOP_sim = False

            if alt > 400 and alt < 420:
                self.fix_alarm = True
            else:
                self.fix_alarm = False

            if alt > 440 and alt < 460:
                self.vibration_alarm = True
            else:
                self.vibration_alarm = False

            """ WIDGETS MUST BE UPDATED in UPDATE_LOCK CONTEXT
                    to prevent concurrent thread access on gui elements
            """
            with self.update_lock:
                self.pfd.set_attitude_pitch(float(pitch))
                self.pfd.set_attitude_orientation(float(yaw))
                self.pfd.set_attitude_roll(float(roll))
                self.pfd.set_altitude(float(alt))
                self.pfd.set_speed(float(speed))
                self.pfd.set_VSI((speed / 3.3) - 10)
                self.pfd.update_attitude()

                self.s.set_text("Sat:19 T:3")
                self.m.set_text(str(mode_array_test[m_ptr]))
                self.t1.set_text(t1_text)
                self.left1.set_text("GS: 29.2")
                self.left2.set_text("wind\ndir: 154\nspd: 5.2")
                self.left3.set_text("Vibrations:\nx:6 y:10 z:12")
                self.left4.set_text("\nThr: 32 %")
                self.t5.set_text("Batt: 23.2V")
                self.t6.set_text("5476 RPM")

            incrementa_number_for_testing += 1
            time.sleep(0.18)

    def on_close(self):
        """ When app closes, the thread gets stopped
        """
        self.thread_alive_flag = False
        super(MyApp, self).on_close()

    def onload(self, emitter):
        """ WebPage Event that occurs on webpage loaded """
        self.execute_javascript("""if (screen.width == 427 && screen.height == 240) {document.body.style.zoom="68%";}""")

if __name__ == "__main__":
    start(Application, address='0.0.0.0', port=8080, multiple_instance=False, start_browser=True, debug=False, update_interval=0.2)
# test