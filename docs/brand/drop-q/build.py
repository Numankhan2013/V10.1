import sys, math, os, json; sys.path.insert(0,'.')
from geo import *
def r2(s):  # round numbers in path
    import re; return re.sub(r'-?\d+\.\d+', lambda m: f"{float(m.group()):.2f}".rstrip('0').rstrip('.'), s)
# --- Drop-Q master geometry (100-unit grid) ---
cx,cy,Ro,Ri,off,dd,r,k,ang = 46,46,36,17,(-2.5,-2.5),44,12.5,12,45
t=math.radians(ang); c2=(cx+dd*math.cos(t), cy+dd*math.sin(t))
RING=r2(circle(cx,cy,Ro)+' '+circle(cx+off[0],cy+off[1],Ri))
DROP=r2(circle(*c2,r)); NECK=r2(neck((cx,cy),Ro,c2,r,k,(1,1)))
# bbox
x0=cx-Ro; x1=c2[0]+r; MC=(x0+x1)/2  # 10 .. ~89.6
OPT=MC-1.2   # optical centre, nudged toward the ring
def mark(fg, extra=''):
    return (f'<g fill="{fg}"{extra}><path fill-rule="evenodd" d="{RING}"/>'
            f'<path d="{NECK}"/><path d="{DROP}"/></g>')
def mark_svg(fg, pad=8, size=None, label='NK QBank Drop-Q mark'):
    s=x1-x0; vb=f"{OPT-s/2-pad:.2f} {OPT-s/2-pad:.2f} {s+2*pad:.2f} {s+2*pad:.2f}"
    wh=f' width="{size}" height="{size}"' if size else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{wh} role="img" aria-label="{label}">{mark(fg)}</svg>'
def icon_svg(bg, fg, size=None, scale=0.56, radius=0.225):
    # 1024-style square; mark spans `scale` of the tile
    S=100; s=x1-x0; sc=S*scale/s
    tx=S/2-OPT*sc; ty=S/2-OPT*sc
    wh=f' width="{size}" height="{size}"' if size else ''
    rr=S*radius
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"{wh} role="img" aria-label="NK QBank app icon">'
            f'<rect width="100" height="100" rx="{rr}" fill="{bg}"/>'
            f'<g transform="translate({tx:.3f} {ty:.3f}) scale({sc:.4f})">{mark(fg)}</g></svg>')
json.dump(dict(RING=RING,DROP=DROP,NECK=NECK,OPT=OPT,x0=x0,x1=x1),open('geom.json','w'))
out='export'; os.makedirs(out,exist_ok=True)
INK='#29263f'; VIOLET='#493394'; PAPER='#fffefd'
files={
 'drop_q_mark_black.svg':mark_svg('#000000'),
 'drop_q_mark_white.svg':mark_svg('#ffffff'),
 'drop_q_mark_ink.svg':mark_svg(INK),
 'drop_q_icon_light.svg':icon_svg(PAPER,INK),
 'drop_q_icon_dark.svg':icon_svg('#15131f','#ffffff'),
 'drop_q_icon_violet.svg':icon_svg(VIOLET,'#ffffff'),
 'drop_q_icon_light_square.svg':icon_svg(PAPER,INK,radius=0),
 'drop_q_icon_violet_square.svg':icon_svg(VIOLET,'#ffffff',radius=0),
}
for n,c in files.items(): open(f'{out}/{n}','w').write(c+'\n')
print(OPT, x0, x1, c2)
