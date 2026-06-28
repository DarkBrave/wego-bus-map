import os

output_dir = "svgs"
os.makedirs(output_dir, exist_ok=True)

SIZE = 200  # square canvas
FONT_SIZE = 120
COLOR = "purple"

for i in range(1, 101):
    svg_content = f'''<svg width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="transparent"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-size="{FONT_SIZE}" fill="{COLOR}" font-family="Arial, sans-serif">
    {i}
  </text>
</svg>'''

    filename = os.path.join(output_dir, f"{i}.svg")
    with open(filename, "w") as f:
        f.write(svg_content)

print("Done: 100 SVG files created in /svgs")
