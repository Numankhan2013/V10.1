# PWA PDF contrast investigation

Status: inspected; no renderer change recommended without device evidence.

The recovered browser renderer already uses the safest high-fidelity path:

- PDF.js renders directly from the authoritative PDF into an opaque canvas.
- Inline crops use a 2–3× device-aware backing raster, bounded only by a 12 MP
  memory ceiling.
- The canvas is displayed at the container width without changing source
  geometry.
- Fullscreen zoom creates a fresh 2,400–3,600 pixel lossless raster rather than
  enlarging the inline canvas.
- No CSS opacity, contrast, brightness, blending, or sharpening filter is
  applied to the PDF canvas.

The reported slightly washed dark text therefore is not explained by an
intentional transparency or color filter in NK QBank. Likely remaining variables
are source-page tone, PDF.js antialiasing, browser canvas color management, and
device downsampling. Blanket contrast or sharpening would also alter pale table
lines, colored diagrams, and source fidelity. Disabling smoothing could make
fine text jagged and inconsistent across browsers.

Decision: preserve the current renderer. A future experiment is allowed only as
an isolated comparison using the same crops at the same CSS and backing sizes on
Android and iPad. It must demonstrate darker text while preserving fine strokes,
pale details, colors, zoom, resolution, and performance. If the result is mixed,
discard it.
