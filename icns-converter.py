from icnsutil import IconFamily

icon = IconFamily()

# PNG dosyalarını iconset boyutlarında ekle
for size in [16, 32, 64, 128, 256, 512, 1024]:
    icon.add_image_file(f'icon.iconset/icon_{size}x{size}.png')

with open('colorsearch.icns', 'wb') as f:
    f.write(icon.tobytes())
