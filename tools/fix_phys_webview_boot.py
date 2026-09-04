from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# The source-PDF renderer is injected before window.QB is constructed.
# Export its functions on window directly so startup cannot dereference
# an as-yet-uninitialised window.QB object.
s = s.replace(
    'onclick="window.QB.openPhysSourceImage(this.querySelector(\'img\'))"',
    'onclick="window.openPhysSourceImage(this.querySelector(\'img\'))"',
)
s = s.replace(
    'window.QB.openPhysSourceImage=openPhysSourceImage;window.QB.closePhysSourceImage=closePhysSourceImage;',
    'window.openPhysSourceImage=openPhysSourceImage;window.closePhysSourceImage=closePhysSourceImage;',
)

p.write_text(s, encoding='utf-8')
print('Fixed Physiology source renderer boot export.')
