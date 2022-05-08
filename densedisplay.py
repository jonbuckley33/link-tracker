import datetime
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import threading

DISPLAY_ROWS=32
DISPLAY_COLUMNS=64
LED_SLOWDOWN_GPIO=4
SMALL_FONT_FILE="/home/pi/rpi-rgb-led-matrix/fonts/5x8.bdf"
MEDIUM_FONT_FILE="/home/pi/rpi-rgb-led-matrix/fonts/6x13.bdf"
MEDIUM_FONT_WIDTH=6
TITLE_COLOR=graphics.Color(243, 139, 0)
NORTH_LABEL_COLOR=graphics.Color(255, 0, 0)
SOUTH_LABEL_COLOR=graphics.Color(255, 255, 255)
PREDICTED_TIME_COLOR=graphics.Color(52, 168, 83)
SCHEDULED_TIME_COLOR=graphics.Color(170, 170, 170)
NO_ARRIVALS_COLOR=graphics.Color(170, 170, 170)
FIRST_LINE_Y_POS=10
SECOND_LINE_Y_POS=25
PADDING_BEFORE_TIME_SUFFIX=2
STARTING_BRIGHTNESS=100  # Out of 100

def _text_for_arrival(direction, arrival):
  if arrival is None:
    return "NONE"
  return "%s min" % _minutes_until_arrival(arrival)

def _minutes_until_arrival(arrival):
  return round((arrival.eta - datetime.datetime.now()).total_seconds() / 60)

def _to_graphics_color(proto_color):
  return graphics.Color(proto_color.r, proto_color.g, proto_color.b)

TICKS_PER_STATE = {
  "BEGINNING_OF_LINE": 90,
  # End of scrolling state is determined by length of text,
  # not number of ticks.
  "SCROLLING": -1,
  "END_OF_LINE": 90,
}

class ScrollingTextDisplay:
  def __init__(self, canvas, start_coordinate, font, color):
    self.canvas = canvas
    self.text = ""
    self.font = font
    self.color = color
    self.start_coordinate = start_coordinate
    self.x = start_coordinate['x']
    self.y = start_coordinate['y']
    self._transition_to_state("BEGINNING_OF_LINE")

  def _transition_to_state(self, state):
    self.state = state
    self.ticks_until_next_state = TICKS_PER_STATE[self.state]

  def _tick(self):
    if self.state == "BEGINNING_OF_LINE":
      if self.ticks_until_next_state <= 0:
        self._transition_to_state("SCROLLING")
    elif self.state == "SCROLLING":
      self.x -= 1
      if self.x + self.text_length < self.canvas.width:
        self._transition_to_state("END_OF_LINE")
    elif self.state == "END_OF_LINE":
      if self.ticks_until_next_state <= 0:
        self.x = self.start_coordinate['x']
        self._transition_to_state("BEGINNING_OF_LINE")
    self.ticks_until_next_state -= 1

  def set_text(self, text):
    self.text = text

  def update(self):
    self._tick()
    self.text_length = graphics.DrawText(self.canvas, self.font, self.x, self.y, self.color, self.text)


class DenseDisplay:
  def __init__(self, display_config):
    self.display_config = display_config

    options = RGBMatrixOptions()
    options.rows = display_config.display_height_pixels
    options.cols = display_config.display_width_pixels
    options.gpio_slowdown = display_config.gpio_slowdown
    options.brightness = STARTING_BRIGHTNESS
    options.pixel_mapper_config = "Rotate:%d" % display_config.display_rotation_degrees

    self.lock = threading.Lock()
    self.matrix = RGBMatrix(options = options)
    self.canvas = self.matrix.CreateFrameCanvas()

    self.small_font = graphics.Font()
    self.small_font.LoadFont(SMALL_FONT_FILE)

    self.medium_font = graphics.Font()
    self.medium_font.LoadFont(MEDIUM_FONT_FILE)

    self.title = ScrollingTextDisplay(
        self.canvas, {'x': 0, 'y': self.small_font.height}, 
        self.small_font, _to_graphics_color(display_config.title_color)
    )
    self.title.set_text("COLUMBIA CITY STATION DEPARTURES")

    self.northbound = None
    self.southbound = None

  def set_next_arrivals(self, northbound, southbound):
    with self.lock:
      self.northbound = northbound
      self.southbound = southbound
   
  def update(self):
    with self.lock:
      self.canvas.Clear()

      self.title.update()

      first_line_y = self.title.y + 11
      graphics.DrawText(
          self.canvas, self.medium_font, 0, first_line_y,
          _to_graphics_color(self.display_config.north_label_color), "North")
      self._draw_arrival(self.northbound, first_line_y)
      
      second_line_y = first_line_y + 12
      graphics.DrawText(
          self.canvas, self.medium_font, 0, second_line_y,
          _to_graphics_color(self.display_config.south_label_color), "South")
      self._draw_arrival(self.southbound, second_line_y)

      self.matrix.SwapOnVSync(self.canvas)

  def set_brightness(self, brightness):
    """Sets the brightness of the display given a [0.0, 1.0] input"""
    with self.lock:
      self.matrix.brightness = brightness * 100

  def clear(self):
    with self.lock:
      self.canvas.Clear()

  def _draw_arrival(self, arrival, y):
    if arrival is None:
      message = "N/A"
      x = self.matrix.width - (len(message) * MEDIUM_FONT_WIDTH)
      graphics.DrawText(
          self.canvas, self.medium_font, x, y, 
          _to_graphics_color(self.display_config.no_arrivals_color), message)
      return

    mins = "%s" % _minutes_until_arrival(arrival)
    suffix = "min"
    color = _to_graphics_color(self.display_config.predicted_time_color if arrival.predicted else self.display_config.scheduled_time_color)
    x = self.canvas.width - (len(mins) * MEDIUM_FONT_WIDTH + PADDING_BEFORE_TIME_SUFFIX + len(suffix) * MEDIUM_FONT_WIDTH)
    graphics.DrawText(self.canvas, self.medium_font, x, y, color, mins)
    x = self.canvas.width - (len(suffix) * MEDIUM_FONT_WIDTH)
    graphics.DrawText(self.canvas, self.medium_font, x, y, color, suffix)
 