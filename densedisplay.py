import datetime
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import threading

DISPLAY_ROWS=32
DISPLAY_COLUMNS=64
LED_SLOWDOWN_GPIO=4
SMALL_FONT_FILE="/home/pi/rpi-rgb-led-matrix/fonts/5x7.bdf"
MEDIUM_FONT_FILE="/home/pi/rpi-rgb-led-matrix/fonts/6x13.bdf"
MEDIUM_FONT_WIDTH=6
TITLE_COLOR=graphics.Color(0, 46, 109)
NORTH_LABEL_COLOR=graphics.Color(255, 0, 0)
SOUTH_LABEL_COLOR=graphics.Color(255, 255, 255)
TIME_COLOR=graphics.Color(214, 7, 142)
FIRST_LINE_Y_POS=10
SECOND_LINE_Y_POS=25
TICKS_BEFORE_SCROLLING = 30

def _text_for_arrival(direction, arrival):
  if arrival is None:
    return "NONE"
  minutes = round((arrival.eta - datetime.datetime.now()).total_seconds() / 60)
  return "%s'" % minutes

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
    options.brightness = 50 # Out of 100

    self.lock = threading.Lock()
    self.matrix = RGBMatrix(options = options)
    self.canvas = self.matrix.CreateFrameCanvas()

    self.small_font = graphics.Font()
    self.small_font.LoadFont(SMALL_FONT_FILE)

    self.medium_font = graphics.Font()
    self.medium_font.LoadFont(MEDIUM_FONT_FILE)

    self.title = ScrollingTextDisplay(self.canvas, {'x': 0, 'y': self.small_font.height}, self.small_font, TITLE_COLOR)
    self.title.set_text("COLUMBIA CITY STATION ARRIVALS")

    self.first_line = "..."
    self.second_line = "..."

  def set_next_arrivals(self, northbound, southbound):
    with self.lock:
      self.first_line = _text_for_arrival("north", northbound)
      self.second_line = _text_for_arrival("south", southbound)

  def update(self):
    with self.lock:
      self.canvas.Clear()

      self.title.update()

      first_line_y = self.title.y + 11
      graphics.DrawText(self.canvas, self.medium_font, 0, first_line_y, NORTH_LABEL_COLOR, "North")
      x = self.canvas.width - (len(self.first_line) * MEDIUM_FONT_WIDTH)
      graphics.DrawText(self.canvas, self.medium_font, x, first_line_y, TIME_COLOR, self.first_line)
      
      second_line_y = first_line_y + 12
      graphics.DrawText(self.canvas, self.medium_font, 0, second_line_y, SOUTH_LABEL_COLOR, "South")
      x = self.canvas.width - (len(self.second_line) * MEDIUM_FONT_WIDTH)
      graphics.DrawText(self.canvas, self.medium_font, x, second_line_y, TIME_COLOR, self.second_line)

      self.matrix.SwapOnVSync(self.canvas)

  def clear(self):
    with self.lock:
      self.canvas.Clear()