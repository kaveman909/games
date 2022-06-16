#!/opt/homebrew/bin/python3

import itertools
from math import pi, floor
import cairo
from PyPDF2 import PdfFileMerger, PdfFileReader
import os


class Color:
  def __init__(self, r, g, b, a=1):
    self.r = nrgb(r)
    self.g = nrgb(g)
    self.b = nrgb(b)
    self.a = a


def set_color(ctx: cairo.Context, color):
  ctx.set_source_rgba(color.r, color.g, color.b, color.a)


def ppi(inches):
  return int(inches * 72)


def nrgb(raw: int):
  return float(raw) / 255


svg = False

GAME_NAME = "Scout"
FONT = "gill sans"

CARD_WIDTH = ppi(2.5)
CARD_HEIGHT = ppi(3.5)

CARD_OUTLINE_WIDTH = 12

PAPER_WIDTH = ppi(11)
PAPER_HEIGHT = ppi(8.5)

MARGIN_WIDTH = ppi(0.5)
MARGIN_HEIGHT = ppi(0.5)

MAX_COLS = floor((PAPER_WIDTH - MARGIN_WIDTH*2)/CARD_WIDTH)
MAX_ROWS = floor((PAPER_HEIGHT - MARGIN_HEIGHT*2)/CARD_HEIGHT)

MAJOR_FONT_SIZE = 50
MAJOR_EXTRA_SHIFT = 8
MINOR_EXTRA_SHIFT = 6

MINOR_FONT_SIZE = 25
BACK_FONT_SIZE = 65

BOX_EXTRA_MARGIN = 20
BOX_RADIUS = (MINOR_FONT_SIZE + 10) / 2
BOX_TOTAL_WIDTH = BOX_RADIUS * 2 + BOX_EXTRA_MARGIN
BOX_EXTRA_Y = 14


def yinv(yin: int):
  return PAPER_HEIGHT - yin


MAIN_TEXT_COLOR = Color(5, 45, 74)
BOX_COLOR = Color(5, 26, 52)
OUTLINE_COLOR = Color(255, 255, 255)
NUMBER_COLORS = [Color(77, 103, 190),
                 Color(0, 142, 226),
                 Color(0, 195, 243),
                 Color(0, 172, 178),
                 Color(67, 222, 98),
                 Color(197, 247, 72),
                 Color(254, 236, 4),
                 Color(255, 190, 30),
                 Color(244, 117, 1),
                 Color(254, 61, 82)]
CARD_BACK_COLOR = Color(0, 0, 0)
CUTS_COLOR = Color(0, 0, 0)

BACK_TRI_LEFT = Color(67, 0, 149)
BACK_TRI_RIGHT = Color(240, 133, 1)
BACK_FONT_COLOR = Color(241, 223, 1)
BACK_LINE_WIDTH = 2


def rot_card(ctx: cairo.Context, xi, yi, angle=pi, inv=False):
  if inv:
    angle = -angle
  xshift = MARGIN_WIDTH + CARD_WIDTH/2 + CARD_WIDTH * xi
  yshift = yinv(MARGIN_HEIGHT + CARD_HEIGHT/2 + CARD_HEIGHT * yi)
  ctx.translate(xshift, yshift)
  ctx.rotate(angle)
  ctx.translate(-xshift, -yshift)


def triangle(ctx: cairo.Context, xi: int, yi: int, color: Color):
  xstart = MARGIN_WIDTH + xi*CARD_WIDTH
  ystart = yinv(MARGIN_HEIGHT + yi*CARD_HEIGHT)
  ctx.move_to(xstart, ystart)
  ctx.rel_curve_to(CARD_WIDTH * 1.25, CARD_HEIGHT * -0.2,
                   CARD_WIDTH * -0.25, CARD_HEIGHT * -0.8, CARD_WIDTH, -CARD_HEIGHT)
  ctx.rel_line_to(-CARD_WIDTH, 0)
  ctx.close_path()
  set_color(ctx, color)
  ctx.fill()


def draw_text(ctx: cairo.Context, main: bool, s, xi: int, yi: int):
  ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD)

  if s == '1':
    extra_shift_major = -4
    extra_shift_minor = MINOR_EXTRA_SHIFT
  else:
    extra_shift_major = MAJOR_EXTRA_SHIFT
    extra_shift_minor = 0
  if main:
    color = MAIN_TEXT_COLOR
    font_size = MAJOR_FONT_SIZE
    ctx.set_font_size(font_size)
    xm = MARGIN_WIDTH + (BOX_TOTAL_WIDTH / 2) - \
        (ctx.text_extents(s).width / 1.5) + extra_shift_major + CARD_WIDTH*xi
    ym = yinv(MARGIN_HEIGHT + CARD_HEIGHT*(yi + 1) - MAJOR_FONT_SIZE - 6)
    line_width = 1
  else:
    color = NUMBER_COLORS[int(s, 16)]
    font_size = MINOR_FONT_SIZE
    ctx.set_font_size(font_size)
    adj = BOX_RADIUS - (2*BOX_RADIUS - ctx.text_extents(s).height) / 2
    xm = MARGIN_WIDTH + (BOX_TOTAL_WIDTH) - 24 - \
        (ctx.text_extents(s).width / 2) + CARD_WIDTH*xi - extra_shift_minor
    ym = yinv(MARGIN_HEIGHT + CARD_HEIGHT*(yi + 1) -
              MAJOR_FONT_SIZE - BOX_RADIUS - adj - BOX_EXTRA_Y)
    line_width = 0.8

  ctx.move_to(xm, ym)
  ctx.text_path(s)

  # set text fill color, fill in the text, preserve so we can draw the outline
  set_color(ctx, color)
  ctx.fill_preserve()
  # Draw thin white outline around text
  ctx.set_line_width(line_width)
  set_color(ctx, OUTLINE_COLOR)

  ctx.stroke()


def draw_back_text(ctx: cairo.Context, s: str, xi: int, yi: int):

  ctx.save()
  ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD)
  ctx.set_font_size(BACK_FONT_SIZE)

  xshift = MARGIN_WIDTH + \
      (CARD_WIDTH - ctx.text_extents(s).height)/2 + CARD_WIDTH * xi
  yshift = yinv(MARGIN_HEIGHT + (CARD_HEIGHT +
                ctx.text_extents(s).width)/2 + CARD_HEIGHT * yi)
  ctx.translate(xshift, yshift)
  ctx.rotate(pi/2)

  ctx.text_path(s)
  # set text fill color, fill in the text, preserve so we can draw the outline
  set_color(ctx, BACK_FONT_COLOR)
  ctx.fill_preserve()
  ctx.set_line_width(BACK_LINE_WIDTH)
  set_color(ctx, OUTLINE_COLOR)

  ctx.stroke()
  ctx.restore()


def draw_box(ctx: cairo.Context, xi: int, yi: int):
  set_color(ctx, BOX_COLOR)
  ctx.set_line_width(0)
  ctx.arc(MARGIN_WIDTH + BOX_RADIUS + BOX_EXTRA_MARGIN + CARD_WIDTH*xi, yinv(MARGIN_HEIGHT +
          CARD_HEIGHT*(yi + 1) - MAJOR_FONT_SIZE - BOX_RADIUS - BOX_EXTRA_Y), BOX_RADIUS, 3*pi/2, pi/2)
  ctx.rel_line_to(-BOX_RADIUS - BOX_EXTRA_MARGIN, 0)
  ctx.rel_line_to(0, -BOX_RADIUS*2)
  ctx.close_path()

  ctx.fill_preserve()
  ctx.stroke()


def draw_outline(ctx: cairo.Context, xi: int, yi: int, fill=False):

  ctx.set_line_width(CARD_OUTLINE_WIDTH)
  set_color(ctx, OUTLINE_COLOR)
  ctx.rectangle(MARGIN_WIDTH + CARD_WIDTH*xi + CARD_OUTLINE_WIDTH/2 - 1, yinv(
      MARGIN_HEIGHT + CARD_HEIGHT*(yi + 1) - CARD_OUTLINE_WIDTH/2 + 1), CARD_WIDTH - CARD_OUTLINE_WIDTH + 2, CARD_HEIGHT - CARD_OUTLINE_WIDTH + 2)

  if fill:
    set_color(ctx, CARD_BACK_COLOR)
    ctx.fill_preserve()

  ctx.set_line_join(cairo.LineJoin.MITER)
  ctx.stroke()


def draw_cuts(ctx: cairo.Context):
  set_color(ctx, CUTS_COLOR)
  ctx.set_line_width(1)

  for i in range(MAX_ROWS + 1):
    # Left side
    ctx.move_to(0, yinv(MARGIN_HEIGHT + CARD_HEIGHT*i))
    ctx.rel_line_to(MARGIN_WIDTH/1.5, 0)

    # Right side
    ctx.move_to(PAPER_WIDTH, yinv(MARGIN_HEIGHT + CARD_HEIGHT*i))
    ctx.rel_line_to(-MARGIN_WIDTH/1.5, 0)

  for i in range(MAX_COLS + 1):
    # Bottom side
    ctx.move_to(MARGIN_WIDTH + CARD_WIDTH*i, yinv(0))
    ctx.rel_line_to(0, -MARGIN_HEIGHT/1.5)

    # Top side
    ctx.move_to(MARGIN_WIDTH + CARD_WIDTH*i, 0)
    ctx.rel_line_to(0, MARGIN_HEIGHT/1.5)

  ctx.stroke()


if __name__ == '__main__':
  xi = 0
  yi = 0
  file_idx = 0

  for left, right in itertools.combinations(range(0, 10), 2):

    if (xi == 0 and yi == 0):
      if svg:
        surface = cairo.SVGSurface(
            'Scout-{}.svg'.format(file_idx), PAPER_WIDTH, PAPER_HEIGHT)
      else:
        surface = cairo.PDFSurface(
            'Scout-{}.pdf'.format(file_idx), PAPER_WIDTH, PAPER_HEIGHT)
        surface_back = cairo.PDFSurface(
            'Scout-Back{}.pdf'.format(file_idx), PAPER_WIDTH, PAPER_HEIGHT)
      file_idx += 1
      ctx = cairo.Context(surface)
      ctx_back = cairo.Context(surface_back)
      draw_cuts(ctx)
      draw_cuts(ctx_back)

    lefts = str(left)
    rights = str(right)

    # Back Side
    # "Flip along short edge"
    xback = xi
    yback = MAX_ROWS - yi - 1
    triangle(ctx_back, xback, yback, BACK_TRI_LEFT)
    rot_card(ctx_back, xback, yback)
    triangle(ctx_back, xback, yback, BACK_TRI_RIGHT)
    rot_card(ctx_back, xback, yback)
    draw_outline(ctx_back, xback, yback)
    draw_back_text(ctx_back, GAME_NAME, xback, yback)

    # Front Left Side
    triangle(ctx, xi, yi, NUMBER_COLORS[left])
    draw_text(ctx, True, lefts, xi, yi)
    draw_box(ctx, xi, yi)
    draw_text(ctx, False, rights, xi, yi)

    rot_card(ctx, xi, yi)

    # Front Rigth Side
    triangle(ctx, xi, yi, NUMBER_COLORS[right])
    draw_text(ctx, True, rights, xi, yi)
    draw_box(ctx, xi, yi)
    draw_text(ctx, False, lefts, xi, yi)

    rot_card(ctx, xi, yi)

    draw_outline(ctx, xi, yi)

    if xi < (MAX_COLS - 1):
      xi += 1
    elif yi < (MAX_ROWS - 1):
      xi = 0
      yi += 1
    else:
      xi = 0
      yi = 0

  surface.finish()
  surface_back.finish()

  # Finally, combine pages of PDF into one
  combined = PdfFileMerger()
  for i in range(0, file_idx):
    combined.append(PdfFileReader('Scout-{}.pdf'.format(i), 'rb'))
    os.remove('Scout-{}.pdf'.format(i))
    combined.append(PdfFileReader('Scout-Back{}.pdf'.format(i), 'rb'))
    os.remove('Scout-Back{}.pdf'.format(i))
  combined.write("Scout.pdf")
