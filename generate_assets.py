"""
Generates polished, multi-resolution app icons for Animated Cursor Buddy.
Produces assets/icon.png and assets/icon.ico (16x16 up to 256x256).
"""

import os
from PIL import Image, ImageDraw


def generate_app_icon():
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 1. Outer rounded shield/squircle background
    margin = 16
    d.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=56,
        fill="#1E1E2E",
        outline="#8AADF4",
        width=8,
    )

    # 2. Glowing inner aura
    d.ellipse([50, 50, 206, 206], fill="#282A36")

    # 3. Stylized mouse cursor arrow
    # Classic pointer polygon points scaled to 256
    cursor_pts = [
        (80, 58),
        (80, 192),
        (124, 154),
        (168, 210),
        (192, 190),
        (148, 136),
        (190, 136),
    ]
    # Drop shadow
    shadow_pts = [(x + 4, y + 6) for x, y in cursor_pts]
    d.polygon(shadow_pts, fill="#11111B")
    # White cursor fill with sleek dark border
    d.polygon(cursor_pts, fill="#F8F8F2", outline="#45475A", width=5)

    # 4. Animated sparkle buddy star above the cursor tip
    star_cx, star_cy = 186, 76
    star_r = 30
    star_pts = [
        (star_cx, star_cy - star_r),
        (star_cx + star_r * 0.32, star_cy - star_r * 0.32),
        (star_cx + star_r, star_cy),
        (star_cx + star_r * 0.32, star_cy + star_r * 0.32),
        (star_cx, star_cy + star_r),
        (star_cx - star_r * 0.32, star_cy + star_r * 0.32),
        (star_cx - star_r, star_cy),
        (star_cx - star_r * 0.32, star_cy - star_r * 0.32),
    ]
    d.polygon(star_pts, fill="#FFD700", outline="#FFA500", width=3)
    # Bright inner sparkle
    d.ellipse([star_cx - 8, star_cy - 8, star_cx + 8, star_cy + 8], fill="#FFFFFF")

    # Save PNG
    png_path = os.path.join(assets_dir, "icon.png")
    img.save(png_path, "PNG")

    # Save Multi-resolution ICO
    ico_path = os.path.join(assets_dir, "icon.ico")
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)

    print(f"Generated icons:\n - {png_path}\n - {ico_path}")


if __name__ == "__main__":
    generate_app_icon()
