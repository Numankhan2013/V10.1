#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageChops, ImageStat


ROOT = Path("app/src/main/assets/source_visuals")


def mean_patch(image: Image.Image, x: float, y: float) -> tuple[int, int, int]:
    w, h = image.size
    cx, cy = int(w*x), int(h*y)
    radius = max(2, int(min(w, h)*0.018))
    box = (max(0, cx-radius), max(0, cy-radius), min(w, cx+radius), min(h, cy+radius))
    return tuple(int(round(v)) for v in ImageStat.Stat(image.crop(box)).mean[:3])


def neutral(color: tuple[int, int, int]) -> bool:
    spread = max(color)-min(color)
    return spread <= 28 and (max(color) <= 48 or min(color) >= 208)


def close(a: tuple[int, int, int], b: tuple[int, int, int]) -> bool:
    return max(abs(a[i]-b[i]) for i in range(3)) <= 18


def dominant_edge(image: Image.Image):
    points=((.03,.03),(.25,.03),(.50,.03),(.75,.03),(.97,.03),(.03,.50),(.97,.50),(.03,.97),(.25,.97),(.50,.97),(.75,.97),(.97,.97))
    colors=[mean_patch(image,x,y) for x,y in points]
    candidates=[c for c in colors if neutral(c)]
    best=None;count=0
    for candidate in candidates:
        n=sum(1 for color in candidates if close(candidate,color))
        if n>count:best,count=candidate,n
    return best if count>=6 else None


def improve(path: Path) -> tuple[bool, bool]:
    image=Image.open(path).convert("RGB")
    w,h=image.size
    if w<60 or h<60:return False,False
    bg=dominant_edge(image)
    cropped=False
    if bg is not None:
        diff=ImageChops.difference(image,Image.new("RGB",image.size,bg)).convert("L")
        mask=diff.point(lambda value:255 if value>20 else 0)
        bbox=mask.getbbox()
        if bbox:
            x0,y0,x1,y1=bbox
            pad=max(5,int(min(w,h)*.035))
            box=(max(0,x0-pad),max(0,y0-pad),min(w,x1+pad),min(h,y1+pad))
            nw,nh=box[2]-box[0],box[3]-box[1]
            removed=1-(nw*nh)/(w*h)
            if nw>=w*.22 and nh>=h*.18 and removed>=.12:
                image=image.crop(box);cropped=True
    upscaled=False
    w,h=image.size
    # Upscaling cannot invent detail, so reserve it for figures where cropping
    # first removed a large PDF canvas. This improves display interpolation
    # without inflating every already-tight source asset in the APK.
    if cropped and max(w,h)<720:
        factor=min(2.5,720/max(w,h))
        if factor>=1.25:
            image=image.resize((round(w*factor),round(h*factor)),Image.Resampling.LANCZOS)
            upscaled=True
    if cropped or upscaled:image.save(path,format="PNG",optimize=False)
    return cropped,upscaled


def main() -> None:
    if not ROOT.is_dir():raise SystemExit("source_visuals directory missing")
    total=crops=upscales=0
    for path in ROOT.rglob("*.png"):
        total+=1
        cropped,upscaled=improve(path)
        crops+=int(cropped);upscales+=int(upscaled)
    if total<10:raise SystemExit(f"Unexpected source visual count: {total}")
    print(f"SOURCE_VISUAL_QUALITY_OK total={total} tight_crops={crops} safe_lanczos_upscales={upscales}")


if __name__=="__main__":main()
