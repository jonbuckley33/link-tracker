from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions

DISPLAY_ROWS=32
DISPLAY_COLUMNS=64
LED_SLOWDOWN_GPIO=4
FONT_FILE="/usr/share/fonts/helvetica-12.bdf"
FIRST_LINE_COLOR=graphics.Color(255, 0, 0)
SECOND_LINE_COLOR=graphics.Color(0, 255, 255)
FIRST_LINE_Y_POS=10
SECOND_LINE_Y_POS=25

class RgbDisplay:
  def __init__(self, *args, **kwargs):
    options = RGBMatrixOptions()
    options.rows = DISPLAY_ROWS
    options.cols = DISPLAY_COLUMNS
    options.gpio_slowdown = LED_SLOWDOWN_GPIO
    self.matrix = RGBMatrix(options = options)
    self.font = graphics.Font()
    self.font.LoadFont(FONT_FILE)
    self.canvas = self.matrix.CreateFrameCanvas()
    self.position = self.canvas.width

    # Display renders two lines of text, one on top
    # of the other.
    self.first_line = ""
    self.second_line = ""

  def set_text(self, first_line, second_line):
    self.first_line = first_line
    self.second_line = second_line

  def update(self):
    self.canvas.Clear()

    top_len = graphics.DrawText(self.canvas, self.font, self.position, FIRST_LINE_Y_POS, FIRST_LINE_COLOR, self.first_line)
    bottom_len = graphics.DrawText(self.canvas, self.font, self.position, SECOND_LINE_Y_POS, SECOND_LINE_COLOR, self.second_line)
    self.position -= 1
    if self.position + max(top_len, bottom_len) < 0:
      self.position = self.canvas.width

    self.matrix.SwapOnVSync(self.canvas)