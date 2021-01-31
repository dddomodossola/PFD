
# -*- coding: utf-8 -*-

from remi.gui import *
from remi import start, App


class untitled(App):
    def __init__(self, *args, **kwargs):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        if not 'editing_mode' in kwargs.keys():
            super(untitled, self).__init__(*args, static_file_path={'my_res':'./res/'})

    def idle(self):
        #idle function called every update cycle
        #self.svg_group.css_transform = "rotate(%sdeg) translate(0px, %spx)"%(self.rotation, self.movement)
        self.svg_group.attributes['transform'] = "rotate(%s 0 0) translate(0 %s)"%(self.rotation, self.movement)
    
    def main(self):
        return untitled.construct_ui(self)
        
    @staticmethod
    def construct_ui(self):
        #DON'T MAKE CHANGES HERE, THIS METHOD GETS OVERWRITTEN WHEN SAVING IN THE EDITOR
        vbox0 = VBox()
        vbox0.attr_class = "VBox"
        vbox0.attr_editor_newclass = False
        vbox0.css_align_items = "center"
        vbox0.css_display = "flex"
        vbox0.css_flex_direction = "column"
        vbox0.css_height = "540.0px"
        vbox0.css_justify_content = "space-around"
        vbox0.css_left = "20px"
        vbox0.css_position = "absolute"
        vbox0.css_top = "20px"
        vbox0.css_width = "645.0px"
        vbox0.variable_name = "vbox0"
        svg0 = Svg()
        svg0.attr_class = "Svg"
        svg0.attr_editor_newclass = False
        svg0.attr_viewBox = "-150 -150 300 300"
        svg0.css_height = "450px"
        svg0.css_order = "-1"
        svg0.css_position = "static"
        svg0.css_top = "20px"
        svg0.css_width = "450px"
        svg0.variable_name = "svg0"
        
        self.svg_group = SvgGroup()
        self.svg_group.attr_class = "SvgGroup"
        self.svg_group.attr_editor_newclass = False
        self.svg_group.css_transform = "rotate(45deg), translate(50, 0)"
        self.svg_group.css_transform_box = "fill-box"
        self.svg_group.css_transform_origin = "center"
        self.svg_group.variable_name = "svg_group"
        green_circle = SvgCircle()
        green_circle.attr_class = "SvgCircle"
        green_circle.attr_cx = "0.0"
        green_circle.attr_cy = "0.0"
        green_circle.attr_editor_newclass = False
        green_circle.attr_fill = "rgb(174,255,85)"
        green_circle.attr_r = "75.0"
        green_circle.variable_name = "green_circle"
        self.svg_group.append(green_circle,'green_circle')
        horizontal_line = SvgLine()
        horizontal_line.attr_class = "SvgLine"
        horizontal_line.attr_editor_newclass = False
        horizontal_line.attr_stroke = "black"
        horizontal_line.attr_stroke_width = "1"
        horizontal_line.attr_x1 = -75.0
        horizontal_line.attr_x2 = 75.0
        horizontal_line.attr_y1 = 0.0
        horizontal_line.attr_y2 = 0.0
        horizontal_line.css_left = "356.45831298828125px"
        horizontal_line.css_top = "270.87846755981445px"
        horizontal_line.variable_name = "horizontal_line"
        self.svg_group.append(horizontal_line,'horizontal_line')
        svg0.append(self.svg_group,'svg_group')
        
        blue_circle = SvgCircle()
        blue_circle.attr_class = "SvgCircle"
        blue_circle.attr_cx = "0.0"
        blue_circle.attr_cy = "0.0"
        blue_circle.attr_editor_newclass = False
        blue_circle.attr_fill_opacity = "0.0"
        blue_circle.attr_r = "105.0"
        blue_circle.attr_stroke = "rgb(41,113,255)"
        blue_circle.attr_stroke_width = "30.0"
        blue_circle.variable_name = "blue_circle"
        svg0.append(blue_circle,'blue_circle')
        
        vbox0.append(svg0,'svg0')
        hbox0 = HBox()
        hbox0.attr_class = "HBox"
        hbox0.attr_editor_newclass = False
        hbox0.css_align_items = "center"
        hbox0.css_display = "flex"
        hbox0.css_flex_direction = "row"
        hbox0.css_justify_content = "space-around"
        hbox0.css_order = "-1"
        hbox0.css_position = "static"
        hbox0.variable_name = "hbox0"
        slider_rotate = Slider()
        slider_rotate.attr_class = "range"
        slider_rotate.attr_editor_newclass = False
        slider_rotate.attr_max = "90"
        slider_rotate.attr_min = "-90"
        slider_rotate.attr_step = "1"
        slider_rotate.attr_value = "-53"
        slider_rotate.css_height = "30px"
        slider_rotate.css_order = "2859883633200"
        slider_rotate.css_position = "static"
        slider_rotate.css_width = "100px"
        slider_rotate.variable_name = "slider_rotate"
        hbox0.append(slider_rotate,'slider_rotate')
        label0 = Label()
        label0.attr_class = "Label"
        label0.attr_editor_newclass = False
        label0.css_order = "-1"
        label0.css_position = "static"
        label0.css_width = "100px"
        label0.text = "Rotation"
        label0.variable_name = "label0"
        hbox0.append(label0,'label0')
        vbox0.append(hbox0,'hbox0')
        hbox1 = HBox()
        hbox1.attr_class = "HBox"
        hbox1.attr_editor_newclass = False
        hbox1.css_align_items = "center"
        hbox1.css_display = "flex"
        hbox1.css_flex_direction = "row"
        hbox1.css_justify_content = "space-around"
        hbox1.css_order = "-1"
        hbox1.css_position = "static"
        hbox1.variable_name = "hbox1"
        slider_movement = Slider()
        slider_movement.attr_class = "range"
        slider_movement.attr_editor_newclass = False
        slider_movement.attr_max = "90"
        slider_movement.attr_min = "-90"
        slider_movement.attr_step = "1"
        slider_movement.attr_value = "54"
        slider_movement.css_height = "30px"
        slider_movement.css_order = "2859883665680"
        slider_movement.css_position = "static"
        slider_movement.css_width = "100px"
        slider_movement.variable_name = "slider_movement"
        hbox1.append(slider_movement,'slider_movement')
        label1 = Label()
        label1.attr_class = "Label"
        label1.attr_editor_newclass = False
        label1.css_order = "-1"
        label1.css_position = "static"
        label1.css_width = "100px"
        label1.text = "Move"
        label1.variable_name = "label1"
        hbox1.append(label1,'label1')
        vbox0.append(hbox1,'hbox1')
        vbox0.children['hbox0'].children['slider_rotate'].onchange.do(self.onchange_slider_rotate)
        vbox0.children['hbox1'].children['slider_movement'].onchange.do(self.onchange_slider_movement)
        
        self.rotation = 0
        self.movement = 0

        self.vbox0 = vbox0
        return self.vbox0
    
    def onchange_slider_rotate(self, emitter, value):
        self.rotation = value

    def onchange_slider_movement(self, emitter, value):
        self.movement = value


#Configuration
configuration = {'config_project_name': 'untitled', 'config_address': '0.0.0.0', 'config_port': 8081, 'config_multiple_instance': False, 'config_enable_file_cache': True, 'config_start_browser': True, 'config_resourcepath': './res/'}

if __name__ == "__main__":
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    start(untitled, address=configuration['config_address'], port=configuration['config_port'], 
                        multiple_instance=configuration['config_multiple_instance'], 
                        enable_file_cache=configuration['config_enable_file_cache'],
                        start_browser=configuration['config_start_browser'])
