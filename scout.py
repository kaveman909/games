#!/opt/homebrew/bin/python3

import itertools
from math import pi
import cairo


class Color:
  def __init__(self, r, g, b):
    self.r = nrgb(r)
    self.g = nrgb(g)
    self.b = nrgb(b)


def ppi(inches):
  return int(inches * 72)


def num_to_index(num):
  return num + 20


def nrgb(raw: int):
  return float(raw) / 255


CARD_WIDTH = ppi(2.5)
CARD_HEIGHT = ppi(3.5)

CARD_OUTLINE_WIDTH = 0

PAPER_WIDTH = ppi(11)
PAPER_HEIGHT = ppi(8.5)

MARGIN_WIDTH = ppi(0.5)
MARGIN_HEIGHT = ppi(0.5)


MAJOR_FONT_SIZE = 54
MAJOR_EXTRA_SHIFT = 10
MINOR_EXTRA_SHIFT = 5

MINOR_FONT_SIZE = 27

BOX_RADIUS = (MINOR_FONT_SIZE + 10) / 2
BOX_EXTRA_MARGIN = 10
BOX_TOTAL_WIDTH = BOX_RADIUS * 2 + BOX_EXTRA_MARGIN


def yinv(yin: int):
  return PAPER_HEIGHT - yin


MAIN_TEXT_COLOR = Color(5, 45, 74)
BOX_COLOR = Color(5, 26, 52)
OUTLINE_COLOR = Color(255, 247, 211)
NUMBER_COLORS = [Color(77, 103, 190),
                 Color(0, 142, 226),
                 Color(0, 195, 243),
                 Color(0, 172, 178),
                 Color(67, 222, 98),
                 Color(197,247,72),
                 Color(254, 236, 4),
                 Color(255, 190, 30),
                 Color(244, 117, 1),
                 Color(254, 61, 82)]


def rot_card(ctx, xi, yi):
  xshift = MARGIN_WIDTH + CARD_WIDTH/2 + CARD_WIDTH * xi
  yshift = yinv(MARGIN_HEIGHT + CARD_HEIGHT/2 + CARD_HEIGHT * yi)
  ctx.translate(xshift, yshift)
  ctx.rotate(pi)
  ctx.translate(-xshift, -yshift)


def triangle(ctx: cairo.Context, xi: int, yi: int, color: Color, alpha=1):
  xstart = MARGIN_WIDTH + xi*CARD_WIDTH
  ystart = yinv(MARGIN_HEIGHT + yi*CARD_HEIGHT)
  ctx.move_to(xstart, ystart)
  ctx.rel_curve_to(CARD_WIDTH * 1.25, CARD_HEIGHT * -0.2,
                   CARD_WIDTH * -0.25, CARD_HEIGHT * -0.8, CARD_WIDTH, -CARD_HEIGHT)
  ctx.rel_line_to(-CARD_WIDTH, 0)
  ctx.close_path()
  ctx.set_source_rgba(color.r, color.g, color.b, alpha)
  ctx.fill()


def draw_text(ctx: cairo.Context, main: bool, s, xi: int, yi: int):
  ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD)

  if s == '1':
    extra_shift_major = 0
    extra_shift_minor = MINOR_EXTRA_SHIFT
  else:
    extra_shift_major = MAJOR_EXTRA_SHIFT
    extra_shift_minor = 0
  if main:
    color = MAIN_TEXT_COLOR
    font_size = MAJOR_FONT_SIZE
    ctx.set_font_size(font_size)
    xm = MARGIN_WIDTH + (BOX_TOTAL_WIDTH / 2) - \
        (ctx.text_extents(s).width / 1) + extra_shift_major + CARD_WIDTH*xi
    ym = yinv(MARGIN_HEIGHT + CARD_HEIGHT*(yi + 1) - MAJOR_FONT_SIZE + 8)
    line_width = 1.6
  else:
    color = NUMBER_COLORS[int(s, 16)]
    font_size = MINOR_FONT_SIZE
    ctx.set_font_size(font_size)
    adj = BOX_RADIUS - (2*BOX_RADIUS - ctx.text_extents(s).height) / 2
    xm = MARGIN_WIDTH + (BOX_TOTAL_WIDTH / 2) - \
        (ctx.text_extents(s).width / 1.5) + CARD_WIDTH*xi - extra_shift_minor
    ym = yinv(MARGIN_HEIGHT + CARD_HEIGHT*(yi + 1) -
              MAJOR_FONT_SIZE - BOX_RADIUS - adj)
    line_width = 1.3

  ctx.move_to(xm, ym)
  ctx.text_path(s)

  # set text fill color, fill in the text, preserve so we can draw the outline
  ctx.set_source_rgb(color.r, color.g, color.b)
  ctx.fill_preserve()
  # Draw thin white outline around text
  ctx.set_line_width(line_width)
  ctx.set_source_rgb(1, 1, 1)

  ctx.stroke()


def draw_box(ctx: cairo.Context, xi: int, yi: int):
  ctx.set_source_rgba(BOX_COLOR.r, BOX_COLOR.g, BOX_COLOR.b)
  ctx.set_line_width(0)
  ctx.arc(MARGIN_WIDTH + BOX_RADIUS + BOX_EXTRA_MARGIN + CARD_WIDTH*xi, yinv(MARGIN_HEIGHT +
          CARD_HEIGHT*(yi + 1) - MAJOR_FONT_SIZE - BOX_RADIUS), BOX_RADIUS, 3*pi/2, pi/2)
  ctx.rel_line_to(-BOX_RADIUS - BOX_EXTRA_MARGIN, 0)
  ctx.rel_line_to(0, -BOX_RADIUS*2)
  ctx.close_path()

  ctx.fill_preserve()
  ctx.stroke()


def draw_outline(ctx: cairo.Context, xi: int, yi: int):
  ctx.set_source_rgba(OUTLINE_COLOR.r, OUTLINE_COLOR.g, OUTLINE_COLOR.b)
  ctx.set_line_width(CARD_OUTLINE_WIDTH)

  ctx.rectangle(MARGIN_WIDTH + CARD_WIDTH*xi, yinv(
      MARGIN_HEIGHT + CARD_HEIGHT*(yi + 1)), CARD_WIDTH, CARD_HEIGHT)

  ctx.set_line_join(cairo.LineJoin.BEVEL)
  ctx.stroke()

# main script
xi = 0
yi = 0
file_idx = 0
for left, right in itertools.combinations(range(0, 10), 2):

  if (xi == 0 and yi == 0):
    # surface = cairo.SVGSurface('Scout-{}.svg'.format(file_idx), PAPER_WIDTH, PAPER_HEIGHT)
    surface = cairo.PDFSurface('Scout-{}.pdf'.format(file_idx), PAPER_WIDTH, PAPER_HEIGHT)
    file_idx += 1
    ctx = cairo.Context(surface)

  lefts = hex(left)[2:].upper()
  rights = hex(right)[2:].upper()

  draw_outline(ctx, xi, yi)

  # Left side of card
  triangle(ctx, xi, yi, NUMBER_COLORS[left])
  draw_text(ctx, True, lefts, xi, yi)
  draw_box(ctx, xi, yi)
  draw_text(ctx, False, rights, xi, yi)

  rot_card(ctx, xi, yi)

  # Rigth Side
  triangle(ctx, xi, yi, NUMBER_COLORS[right])
  draw_text(ctx, True, rights, xi, yi)
  draw_box(ctx, xi, yi)
  draw_text(ctx, False, lefts, xi, yi)

  rot_card(ctx, xi, yi)

  if xi < 3:
    xi += 1
  elif yi < 1:
    xi = 0
    yi += 1
  else:
    xi = 0
    yi = 0
