"""
image_generator.py
Builds a branded "Trendora" deal-card image for Telegram + Instagram
using the product photo, MRP, selling price and discount percentage.
"""

import io
import os
import logging
import requests
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")

CANVAS_SIZE = (1080, 1350)  # Instagram portrait-friendly size
BG_COLOR = (10, 10, 10)
PINK = (233, 30, 99)
ORANGE = (255, 140, 40)
WHITE = (255, 255, 255)


def _font(size, bold=True):
    """Falls back to default PIL font if no truetype font is available."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _gradient_bar(draw, xy, color1, color2):
    x0, y0, x1, y1 = xy
    width = x1 - x0
    for i in range(width):
        ratio = i / max(width - 1, 1)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(x0 + i, y0), (x0 + i, y1)], fill=(r, g, b))


def _load_product_image(image_url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    resp = requests.get(image_url, headers=headers, timeout=15)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "image" not in content_type:
        raise ValueError(f"URL image nahi hai (Content-Type: {content_type}): {image_url}")
    return Image.open(io.BytesIO(resp.content)).convert("RGBA")


def generate_deal_image(product_name, image_url, mrp, price, discount_percent, output_path):
    canvas = Image.new("RGB", CANVAS_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Top gradient bar
    _gradient_bar(draw, (0, 0, CANVAS_SIZE[0], 18), PINK, ORANGE)

    # Logo top-left
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((140, 140))
        canvas.paste(logo, (40, 40), logo)

    # Product image, centered
    try:
        product_img = _load_product_image(image_url)
        product_img.thumbnail((760, 620))
        px = (CANVAS_SIZE[0] - product_img.width) // 2
        canvas.paste(product_img, (px, 220), product_img)
    except Exception as e:
        logger.warning(f"Product image load failed: {e}")
        draw.rectangle([160, 220, 920, 840], outline=WHITE, width=3)
        draw.text((400, 500), "Image N/A", font=_font(36), fill=WHITE)

    # Discount badge (top-right)
    badge_font = _font(46)
    badge_text = f"-{int(discount_percent)}%"
    draw.ellipse([880, 40, 1040, 200], fill=(233, 30, 60))
    tw = draw.textlength(badge_text, font=badge_font)
    draw.text((960 - tw / 2, 95), badge_text, font=badge_font, fill=WHITE)

    # Product name
    name_font = _font(42)
    name = product_name if len(product_name) <= 55 else product_name[:52] + "..."
    draw.text((60, 890), name, font=name_font, fill=WHITE)

    # Price block
    price_font = _font(64)
    mrp_font = _font(38)
    draw.text((60, 970), f"₹{int(price):,}", font=price_font, fill=(80, 220, 120))
    mrp_text = f"₹{int(mrp):,}"
    mtw = draw.textlength(mrp_text, font=mrp_font)
    mrp_x = 60 + draw.textlength(f"₹{int(price):,}", font=price_font) + 30
    draw.text((mrp_x, 995), mrp_text, font=mrp_font, fill=(150, 150, 150))
    draw.line(
        [(mrp_x - 5, 1015), (mrp_x + mtw + 5, 1015)],
        fill=(150, 150, 150),
        width=3,
    )

    # Bottom tagline bar
    _gradient_bar(draw, (0, 1260, CANVAS_SIZE[0], 1278), PINK, ORANGE)
    tag_font = _font(30)
    draw.text((60, 1290), "TRENDORA  •  Daily Deals. Best Finds.", font=tag_font, fill=WHITE)

    canvas.save(output_path, quality=95)
    return output_path