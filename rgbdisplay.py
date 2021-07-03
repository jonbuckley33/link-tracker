from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import threading

DISPLAY_ROWS=32
DISPLAY_COLUMNS=64
LED_SLOWDOWN_GPIO=4
FONT_FILE="/usr/share/fonts/helvetica-12.bdf"
FIRST_LINE_COLOR=graphics.Color(255, 0, 0)
SECOND_LINE_COLOR=graphics.Color(0, 255, 255)
FIRST_LINE_Y_POS=10
SECOND_LINE_Y_POS=25
TICKS_BEFORE_SCROLLING = 30

def _text_for_arrival(direction, arrival):
  if arrival is None:
    return "No %s train scheduled :(" % direction
  return "Next train %s: %s" % (direction, arrival.eta.strftime("%X"))

TICKS_PER_STATE = {
  "BEGINNING_OF_LINE": 90,
  # End of scrolling state is determined by length of text,
  # not number of ticks.
  "SCROLLING": -1,
  "END_OF_LINE": 90,
}

class RgbDisplay:
  def __init__(self, *args, **kwargs):
    options = RGBMatrixOptions()
    options.rows = DISPLAY_ROWS
    options.cols = DISPLAY_COLUMNS
    options.gpio_slowdown = LED_SLOWDOWN_GPIO

    self.lock = threading.Lock()
    self.matrix = RGBMatrix(options = options)
    self.font = graphics.Font()
    self.font.LoadFont(FONT_FILE)
    self.canvas = self.matrix.CreateFrameCanvas()
    self.position = 0
    self._transition_to_state("BEGINNING_OF_LINE")
    self.text_length = 0

    # Display renders two lines of text, one on top
    # of the other.
    self.first_line = ""
    self.second_line = ""

  def set_next_arrivals(self, northbound, southbound):
    with self.lock:
      self.first_line = _text_for_arrival("north", northbound)
      self.second_line = _text_for_arrival("south", southbound)

  def _transition_to_state(self, state):
    self.state = state
    self.ticks_until_next_state = TICKS_PER_STATE[self.state]

  def _tick(self):
    if self.state == "BEGINNING_OF_LINE":
      if self.ticks_until_next_state <= 0:
        self._transition_to_state("SCROLLING")
    elif self.state == "SCROLLING":
      self.position -= 1
      if self.position + self.text_length < self.canvas.width:
        self._transition_to_state("END_OF_LINE")
    elif self.state == "END_OF_LINE":
      if self.ticks_until_next_state <= 0:
        self.position = 0
        self._transition_to_state("BEGINNING_OF_LINE")
    self.ticks_until_next_state -= 1

  def update(self):
    with self.lock:
      self._tick()

      self.canvas.Clear()
      top_len = graphics.DrawText(self.canvas, self.font, self.position, FIRST_LINE_Y_POS, FIRST_LINE_COLOR, self.first_line)
      bottom_len = graphics.DrawText(self.canvas, self.font, self.position, SECOND_LINE_Y_POS, SECOND_LINE_COLOR, self.second_line)
      self.text_length = max(top_len, bottom_len)
      self.matrix.SwapOnVSync(self.canvas)

  def clear(self):
    with self.lock:
      self.canvas.Clear()