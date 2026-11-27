"""bridge shot -> left eye, cropped to the gun area, enlarged and brightened. python shot_zoom.py <out.png> [gain]"""
import os, subprocess, sys
from PIL import Image, ImageEnhance
CLI = os.path.expanduser("~/github-backups/mcp-game-bridge-cubed/tools/bridge_cli.py")
out = sys.argv[1]; gain = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
raw = out[:-4] + "_raw.png"
subprocess.run([sys.executable, CLI, "hardreset.exe", "shot", raw, "1.0"], capture_output=True)
im = Image.open(raw).convert("RGB"); w, h = im.size
l = im.crop((0, 0, w // 2, h)); lw, lh = l.size
c = l.crop((int(lw * 0.10), int(lh * 0.22), lw, int(lh * 0.75)))
c = c.resize((1100, int(1100 * c.size[1] / c.size[0])), Image.LANCZOS)
ImageEnhance.Brightness(c).enhance(gain).save(out)
