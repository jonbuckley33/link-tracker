from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time

DISPLAY_ROWS=32
DISPLAY_COLUMNS=64
LED_SLOWDOWN_GPIO=4
FONT_FILE="/usr/share/fonts/helvetica-12.bdf"
TEXT_COLOR=graphics.Color(255, 255, 0)
Y_OFFSET=10

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
    self.text = ""
    self.position = self.canvas.width

  def set_text(self, text):
    self.text = text

  def update(self):
    self.canvas.Clear()

    len = graphics.DrawText(self.canvas, self.font, self.position, Y_OFFSET, TEXT_COLOR, self.text)
    self.position -= 1
    if self.position + len < 0:
      self.position = self.canvas.width

    self.matrix.SwapOnVSync(self.canvas)