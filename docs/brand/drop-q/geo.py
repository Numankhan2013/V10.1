import math
def pt(cx,cy,r,a):  # a in degrees, 0=east, clockwise (svg y down)
    t=math.radians(a); return (cx+r*math.cos(t), cy+r*math.sin(t))
def f(p): return f"{p[0]:.2f} {p[1]:.2f}"
def ring_seg(cx,cy,r,w,a0,a1,cap='round'):
    """filled annulus segment from a0 to a1 clockwise, centerline radius r, width w"""
    ro, ri = r+w/2, r-w/2
    sweep=(a1-a0)%360
    large=1 if sweep>180 else 0
    o0,o1=pt(cx,cy,ro,a0),pt(cx,cy,ro,a1)
    i0,i1=pt(cx,cy,ri,a0),pt(cx,cy,ri,a1)
    c=w/2
    if cap=='round':
        return (f"M{f(o0)} A{ro} {ro} 0 {large} 1 {f(o1)} A{c} {c} 0 0 1 {f(i1)} "
                f"A{ri} {ri} 0 {large} 0 {f(i0)} A{c} {c} 0 0 1 {f(o0)} Z")
    return (f"M{f(o0)} A{ro} {ro} 0 {large} 1 {f(o1)} L{f(i1)} "
            f"A{ri} {ri} 0 {large} 0 {f(i0)} Z")
def ring(cx,cy,r,w):
    ro,ri=r+w/2,r-w/2
    return (f"M{cx-ro} {cy} a{ro} {ro} 0 1 0 {2*ro} 0 a{ro} {ro} 0 1 0 {-2*ro} 0 Z "
            f"M{cx-ri} {cy} a{ri} {ri} 0 1 1 {2*ri} 0 a{ri} {ri} 0 1 1 {-2*ri} 0 Z")
def circle(cx,cy,r): return f"M{cx-r} {cy} a{r} {r} 0 1 0 {2*r} 0 a{r} {r} 0 1 0 {-2*r} 0 Z"
def capsule(x0,y0,x1,y1,w):
    a=math.atan2(y1-y0,x1-x0); n=(-math.sin(a)*w/2, math.cos(a)*w/2); c=w/2
    p0=(x0+n[0],y0+n[1]); p1=(x1+n[0],y1+n[1]); p2=(x1-n[0],y1-n[1]); p3=(x0-n[0],y0-n[1])
    return f"M{f(p0)} L{f(p1)} A{c} {c} 0 0 0 {f(p2)} L{f(p3)} A{c} {c} 0 0 0 {f(p0)} Z"
def neck(c1,R,c2,r,k,sw=(0,0)):
    """metaball connector between circle (c1,R) and (c2,r) with fillet radius k"""
    import math
    dx,dy=c2[0]-c1[0],c2[1]-c1[1]; d=math.hypot(dx,dy); ux,uy=dx/d,dy/d
    a,b=R+k,r+k
    x=(a*a-b*b+d*d)/(2*d); h=math.sqrt(max(a*a-x*x,0))
    res=[]
    for s in (1,-1):
        P=(c1[0]+ux*x-s*uy*h, c1[1]+uy*x+s*ux*h)
        tA=(c1[0]+(P[0]-c1[0])*R/a, c1[1]+(P[1]-c1[1])*R/a)
        tB=(c2[0]+(P[0]-c2[0])*r/b, c2[1]+(P[1]-c2[1])*r/b)
        res.append((tA,tB))
    (a1,b1),(a2,b2)=res
    return (f"M{f(a1)} A{k} {k} 0 0 {sw[0]} {f(b1)} L{f(b2)} A{k} {k} 0 0 {sw[1]} {f(a2)} Z")
