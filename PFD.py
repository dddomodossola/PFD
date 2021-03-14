
# -*- coding: utf-8 -*-

from remi import gui
from remi import start, App
import math
import threading
import time


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
                    self.widget_layout_map[widget_key] = { 'width': "%.2f%%"%float(widget_width / (row_width) * 100.0 - gap_horizontal), 
                                            'height':1, 
                                            'top':"%.2f%%"%float(row_index / (layout_height_in_chars) * 100.0 + (gap_vertical/2.0)), 
                                            'left':"%.2f%%"%float(left_value / (row_width) * 100.0 + (gap_horizontal/2.0))}
                else:
                    self.widget_layout_map[widget_key]['height'] += 1
                
                left_value += widget_width
            row_index += 1

        #converting height values in percent string
        for key in self.widget_layout_map.keys():
            self.widget_layout_map[key]['height'] = "%.2f%%"%float(self.widget_layout_map[key]['height'] / (layout_height_in_chars) * 100.0 - gap_vertical) 

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
        self.children[widget_key].set_size(self.widget_layout_map[widget_key]['width'], self.widget_layout_map[widget_key]['height'])
        self.children[widget_key].css_left = self.widget_layout_map[widget_key]['left']
        self.children[widget_key].css_top = self.widget_layout_map[widget_key]['top']


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

    def __init__(self, x_pos, y_pos, wide, high, left_side, scale_length, scale_length_visible, *args, **kwargs):
        """ x_pos and y_pos are coordinates indicated by the pointer, generally at the center of the shown tape
        """
        gui.SvgGroup.__init__(self, *args, **kwargs)

        self.scale_length = scale_length
        self.scale_length_visible = scale_length_visible

        self.wide = wide
        self.high = high

        self.indicator_size = self.wide*0.2
        self.left_side = left_side
        
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

        self.pointer_value = gui.SvgText(((0-self.indicator_size) if self.left_side else (self.wide-0.05*self.wide)), 0, "%d"%(self.value%360))
        self.pointer_value.attr_dominant_baseline = 'middle'
        self.pointer_value.attr_text_anchor = 'end' if self.left_side else 'end'
        self.pointer_value.set_fill('orange')
        self.pointer_value.css_font_size = gui.to_pix(0.3*self.wide)
        self.pointer_value.css_font_weight = 'bolder'
        #self.pointer_value.attributes['transform'] = 'translate(0 %s)'%(self.vh/2-0.11*self.vh)
        self.append(self.pointer_value)

    def build_scale(self):
        self.group_scale.empty()

        #horizontal line along all the tape size
        x = self.wide/2 if self.left_side else -self.wide/2
        line = gui.SvgLine(x, -self.value-self.scale_length_visible/2, x, -self.value+self.scale_length_visible/2)
        line.set_stroke(0.1*self.wide, 'gray')
        self.group_scale.append(line)

        #creating labels
        labels = {}
        labels_size = {}
        step = 10
        for i in range(int(self.value/step -1 -(self.scale_length_visible/step)/2), int(self.value/step + (self.scale_length_visible/step)/2+1)):
            if not i*step in labels.keys():
                labels[i*step] = "%d"%(i*step) 
                labels_size[i*step] = 1.0

        indicator_x =  (self.wide/2-self.indicator_size) if self.left_side else (-self.wide/2+self.indicator_size)
        text_x = ((self.wide/2-self.indicator_size) if self.left_side else (self.wide/2-0.05*self.wide))
        content = ""
        for v in range(int(self.value-self.scale_length_visible/2), int(self.value+self.scale_length_visible/2 +1)):
            if v in labels.keys():
                y = -v
                """line = gui.SvgLine(indicator_x, y, self.wide/2 if self.left_side else -self.wide/2, y)
                line.set_stroke(0.03*self.wide, 'gray')
                self.group_scale.append(line)
                """
                content += """<line class="SvgLine" x1="%(x1)s" y1="%(y1)s" x2="%(x2)s" y2="%(y2)s" stroke="gray" stroke-width="0.6"></line>"""%{'x1':indicator_x, 'y1':y, 'x2':(self.wide/2 if self.left_side else -self.wide/2), 'y2':y}

                content += """<text class="SvgText" x="%(x)s" y="%(y)s" fill="white" style="dominant-baseline:middle;text-anchor:end;font-size:%(font)s;font-weight:bolder">%(text)s</text>"""%{'x':text_x, 'y':y, 'text':labels.get(v, ''), 'font':gui.to_pix(0.28*self.wide) }
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

                txt = gui.SvgText(x, y, labels.get(angle%360, ''))
                txt.attr_dominant_baseline = 'hanging'
                txt.attr_text_anchor = 'middle'
                txt.set_fill('white')
                txt.css_font_size = gui.to_pix(7*labels_size[angle%360])
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
        self.orientation_tape = OrientationTapeHorizontal(0, 0.4*self.vh, 0.8*self.vw, 1.0*self.vh)
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
                content += """<text class="SvgText" x="%(x)s" y="%(y)s" fill="rgba(255,255,255,0.5)" style="dominant-baseline:middle;text-anchor:start;font-size:4.0px">%(text)s</text>"""%{'x':sign_size/2, 'y':y, 'text':str(int(angle))}
                content += """<text class="SvgText" x="%(x)s" y="%(y)s" fill="rgba(255,255,255,0.5)" style="dominant-baseline:middle;text-anchor:end;font-size:4.0px">%(text)s</text>"""%{'x':-sign_size/2, 'y':y, 'text':str(int(angle))}
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
        background = gui.SvgRectangle(-100, -50, 200, 100)
        background.set_fill('black')
        self.append(background)

        self.attitude_indicator = AttitudeIndicator()
        self.append(self.attitude_indicator)

        self.speed_indicator = TapeVertical(-51, 0, 20, 80, True, 999, 100) #three digits values
        self.append(self.speed_indicator)

        self.altitude_indicator = TapeVertical(51, 0, 20, 80, False, 9999, 100) #four digits values
        self.append(self.altitude_indicator)

        #x_pos, y_pos, wide, high, left_side, scale_length, scale_length_visible
        self.VSI_indicator = TapeVertical(75, 0, 10, 50, False, 100, 30)
        self.append(self.VSI_indicator)

    def set_attitude_pitch(self, value):
        self.attitude_indicator.set_pitch(value)

    def set_attitude_orientation(self, value):
        self.attitude_indicator.set_orientation(value)
        self.speed_indicator.set_value(value)

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


class Application(App):
    color_flipper = None
    standard_label_color = 'orange'

    thread_alive_flag = False

    ab = 0.1

    def idle(self):
        #idle function called every update cycle
        #self.svg_group.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.rotation, self.movement)

        #just an example
        battery_is_low = True
        if battery_is_low:
            self.t5.css_color = self.color_flipper[0]
        else:
            self.t5.css_color = self.standard_label_color

        #swap colors each update
        self.color_flipper = [self.color_flipper[1],self.color_flipper[0]]
        
    def main(self):
        self.color_flipper = ['orange', 'white']

        centering_container = gui.Container(width=640, height=360, style={'background-color':'black', "position":"fixed"})

        #to make a left margin or 50px (because of google glasses curvature), I have to calculate a new height
        _w_margin  = 50
        _h_margin = _w_margin*360/640
        self.main_container = AsciiContainer(width=640-_w_margin, height=360-_h_margin, style={'background-color':'black','margin-left':gui.to_pix(_w_margin), 'margin-top':gui.to_pix(_h_margin/2)})

        self.main_container.set_from_asciiart("""
        | t0                                                                                                     |
        | left1        | pfd                                                                                     |
        | left1        | pfd                                                                                     |
        | left1        | pfd                                                                                     |
        | left2        | pfd                                                                                     |
        | left2        | pfd                                                                                     |
        | left2        | pfd                                                                                     |
        | left3        | pfd                                                                                     |
        | left3        | pfd                                                                                     |
        | left3        | pfd                                                                                     |
        | left4        | pfd                                                                                     |
        | left4        | pfd                                                                                     |
        | left4        | pfd                                                                                     |
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
        self.pfd = PrimaryFlightDisplay(style={'position':'absolute'})
        _style = {'text-align':'center', 'color':self.standard_label_color, 'outline':'1px solid black'}
        self.t0 =       gui.Label("T0",     style=_style)
        self.t1 =       gui.Label("T1",     style=_style)
        self.t5 =       gui.Label("T5",     style=_style)
        self.t6 =       gui.Label("T6",     style=_style)
        self.s =        gui.Label("S",      style=_style)
        self.m =        gui.Label("M",      style=_style)
        self.left1 =    gui.Label("left1",  style=_style)
        self.left2 =    gui.Label("left2",  style=_style)
        self.left3 =    gui.Label("left3",  style=_style)
        self.left4 =    gui.Label("left4",  style=_style)

        self.main_container.append(self.pfd, "pfd")
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
    
        # Here I start a parallel thread
        self.thread_alive_flag = True
        t = threading.Thread(target=self.my_threaded_function)
        t.start()

        centering_container.append(self.main_container)
        return centering_container

    def my_threaded_function(self):
        while self.thread_alive_flag:
            #calculations
            self.ab +=0.5
            if self.ab > 70: self.ab=-70

            pitch=self.ab
            yaw=self.ab*2
            roll=self.ab
            alt=abs(self.ab*1.5+400)
            speed=abs(self.ab)

            """ WIDGETS MUST BE UPDATED in UPDATE_LOCK CONTEXT
                    to prevent concurrent thread access on gui elements
            """
            with self.update_lock:
                self.pfd.set_attitude_pitch(float(pitch))
                self.pfd.set_attitude_orientation(float(yaw))
                self.pfd.set_attitude_roll(float(roll))
                self.pfd.set_altitude(float(alt))
                self.pfd.set_speed(float(speed))
                self.pfd.update_attitude()

                self.s.set_text("Fix3 HDOP: 0.7")
                self.m.set_text("STABILIZED")
                self.t1.set_text("pitch" + str(pitch) + " roll" + str(roll))
                self.left1.set_text("Gen:   25.5v")
                self.left2.set_text("TESTING_LONG_STRING")
                self.left3.set_text("Next line \n here")
                self.t5.set_text("Batt: 23.2V")

            time.sleep(0.2)

    def on_close(self):
        """ When app closes, the thread gets stopped
        """
        self.thread_alive_flag = False
        super(MyApp, self).on_close()


if __name__ == "__main__":
    start(Application, address='0.0.0.0', port=8080, multiple_instance=False, start_browser=True, debug=False, update_interval=0.2)
