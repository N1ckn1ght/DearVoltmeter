import dearpygui.dearpygui as dpg
import random
import numpy as np
import time
from PIL import Image


class Data():
    window_width = 400
    window_height = 396
    image_width = 367
    image_height = 50
    

def formated(value):
    return ("%06.2f" % value) + "V"


def voltage(value, screenVoltage, screenImage):
    dpg.set_value(screenVoltage, formated(value))
    tag = "wide_" + str(max(0, min(int(value * 10), 3615)))
    dpg.configure_item(screenImage, texture_tag=tag)


def show_average(sender, app_data, user_data):
    global averages
    global timeCurrent
    global timeMax
    global threshold
    time_   = float(dpg.get_value(user_data[0]))
    field   = user_data[1]
    
    sum = 0
    realDiv = 0
    expcDiv = int(time_ / threshold)
    count = min(expcDiv, timeCurrent)
    print("Debug |", timeCurrent, timeMax, threshold, time_)
    print("First chunk of elements =", count)
    for i in range(timeCurrent - 1, timeCurrent - count - 1, -1):
        if (averages[i] == -1):
            print("Error: not enough data! Break on", i)
            break
        realDiv += 1
        sum += averages[i]
    count = expcDiv - count
    print("Second chunk of elements =", count)
    for i in range(timeMax - 1, timeMax - 1 - count, -1):
        if (averages[i] == -1):
            print("Error: not enough data! Break on", i)
            break
        realDiv += 1
        sum += averages[i]
    print("Total chunk of elements =", realDiv)
    print("Sum of measurements = ", sum)
    print("Note: 1 elem = ", threshold, "seconds\n")

    if (realDiv > 0):
        dpg.set_value(field, formated(float(sum) / realDiv))
    

dpg.create_context()
dpg.create_viewport(title="Barbie's Dear Voltmeter", width=Data.window_width, height=Data.window_height, resizable=False)

with dpg.font_registry():
    default_font = dpg.add_font(f'fonts\consola.ttf', 24)
    volt_font    = dpg.add_font(f'fonts\consola.ttf', 92)
    small_font   = dpg.add_font(f'fonts\consola.ttf', 19)

with dpg.texture_registry():
    for i in range(0, 3615, 1):
        width, height, _, data = dpg.load_image(f"res/wide_{i}.png")
        scale_tag = f"wide_{i}"
        dpg.add_static_texture(width=Data.image_width, height=Data.image_height, default_value=data, tag=scale_tag)

fulltime = time.perf_counter()
timestamp = 0
threshold = 0.1
initials = [3.3, 5, 12, 24, 230]
initialV = initials[random.randint(0, 4)]
distr    = float(random.randint(1, 8)) / 10

timeMax = int(60 / threshold)
timeCurrent = 0
averages = [-1 for i in range(timeMax)]

with dpg.window(tag="main"):
    with dpg.group():
        cv = dpg.add_input_text(default_value="000.00V", width=-1, readonly=True, enabled=False)
        im = dpg.add_image(texture_tag="wide_0")
        dpg.add_spacer(height=20)
        tx = dpg.add_text(default_value="Average voltage in last _ seconds:")
        with dpg.group(horizontal=True):
            sc = dpg.add_input_int(default_value=1, width=273, min_value=1, max_value=60, min_clamped=True, max_clamped=True)
            go = dpg.add_button(label="Show", width=90, callback=show_average, user_data=(sc, "cv2"))
        cv2 = dpg.add_input_text(tag = "cv2", default_value="", width=-1, readonly=True, enabled=False)
    dpg.bind_font(default_font)
    dpg.bind_item_font(cv, volt_font)
    dpg.bind_item_font(cv2, volt_font)
    dpg.bind_item_font(tx, small_font)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 179, 198), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, (255, 179, 198), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 229, 236), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (251, 111, 146), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (251, 111, 146), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 143, 171), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (251, 111, 146), category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvText):
         dpg.add_theme_color(dpg.mvThemeCol_Text, (251, 111, 146), category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)

while dpg.is_dearpygui_running():
    timestamp = time.perf_counter() - fulltime
    if (timestamp > threshold):
        fulltime += threshold
        timestamp -= threshold
        v = np.random.normal(initialV, distr, 1)[0]
        voltage(v, cv, im)
        averages[timeCurrent] = v
        timeCurrent += 1
        if (timeCurrent == timeMax):
            timeCurrent = 0
    dpg.render_dearpygui_frame()

dpg.destroy_context()
