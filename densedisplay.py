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
BRIGHTNESS=100  # Out of 100

def _text_for_arrival(direction, arrival):
  if arrival is None:
    return "NONE"
  return "%s min" % _minutes_until_arrival(arrival)

def _minutes_until_arrival(arrival):
  return round((arrival.eta - datetime.datetime.now()).total_seconds() / 60)

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
  def __init__(self, *args, **kwargs):
    options = RGBMatrixOptions()
    options.rows = DISPLAY_ROWS
    options.cols = DISPLAY_COLUMNS
    options.gpio_slowdown = LED_SLOWDOWN_GPIO
    options.brightness = BRIGHTNESS

    self.lock = threading.Lock()
    self.matrix = RGBMatrix(options = options)
    self.canvas = self.matrix.CreateFrameCanvas()

    self.small_font = graphics.Font()
    self.small_font.LoadFont(SMALL_FONT_FILE)

    self.medium_font = graphics.Font()
    self.medium_font.LoadFont(MEDIUM_FONT_FILE)

    self.title = ScrollingTextDisplay(self.canvas, {'x': 0, 'y': self.small_font.height}, self.small_font, TITLE_COLOR)
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
      graphics.DrawText(self.canvas, self.medium_font, 0, first_line_y, NORTH_LABEL_COLOR, "North")
      self._draw_arrival(self.northbound, first_line_y)
      
      second_line_y = first_line_y + 12
      graphics.DrawText(self.canvas, self.medium_font, 0, second_line_y, SOUTH_LABEL_COLOR, "South")
      self._draw_arrival(self.southbound, second_line_y)

      self.matrix.SwapOnVSync(self.canvas)

  def clear(self):
    with self.lock:
      self.canvas.Clear()

  def _draw_arrival(self, arrival, y):
    if arrival is None:
      message = "N/A"
      x = self.matrix.width - (len(message) * MEDIUM_FONT_WIDTH)
      graphics.DrawText(self.canvas, self.medium_font, x, y, NO_ARRIVALS_COLOR, message)
      return

    mins = "%s" % _minutes_until_arrival(arrival)
    suffix = "min"
    color = PREDICTED_TIME_COLOR if arrival.predicted else SCHEDULED_TIME_COLOR
    x = self.canvas.width - (len(mins) * MEDIUM_FONT_WIDTH + PADDING_BEFORE_TIME_SUFFIX + len(suffix) * MEDIUM_FONT_WIDTH)
    graphics.DrawText(self.canvas, self.medium_font, x, y, color, mins)
    x = self.canvas.width - (len(suffix) * MEDIUM_FONT_WIDTH)
    graphics.DrawText(self.canvas, self.medium_font, x, y, color, suffix)
 