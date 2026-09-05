# V11 Source Visuals

## Contract
Every question and option may independently declare an optional `visual` object. The renderer must consume metadata, never question-number heuristics.

```js
visual: {
  type: "source-pdf",
  source: "Anatomy_QBank_Source.pdf",
  page: 1852,
  crop: { left: 0, top: 0, right: 612, bottom: 792 },
  fit: "contain"
}
```

`crop` is optional and expressed in source-PDF points. `fit` is `contain`, `width`, or `native`.

## Interaction requirements
- high-resolution source rendering
- aspect-ratio preserving
- bounded pan
- focal-point pinch zoom
- double-tap zoom
- zoom +/-
- reset-to-fit
- no image loss beyond recoverable bounds
- image gestures must not fight question/page scrolling
- full-screen viewer for detailed anatomy/histology inspection

## Subject isolation
- Anatomy -> Anatomy source PDF
- Biochemistry -> Biochemistry source PDF
- Physiology -> Physiology source PDF

Existing explanation renderers remain isolated unless deliberately migrated.
