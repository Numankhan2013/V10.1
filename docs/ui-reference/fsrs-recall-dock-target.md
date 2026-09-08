# FSRS Recall Dock — Approved Visual Target

**Status:** User-approved UI target — 2026-09-07  
**Reference:** `fsrs-recall-dock-target.jpg`  
**Scope:** Post-answer FSRS recall-rating dock only; phone-first Android/PWA.

## Visual source of truth

The sibling JPG is a focused crop of the approved Android mockup. Treat it as the visual source of truth for the recall dock. It is intentionally cropped tightly around the Key Takeaway, recall selector, and Previous/Next area so an implementation agent does not infer a wider redesign.

The image is a reference asset only. Do **not** ship it in the APK/PWA.

## Placement

- Put the recall-rating dock immediately above the existing **Previous / Next** navigation.
- Keep the current narrow Android-phone proportions and content margins.
- Do not widen the screen into a tablet/iPad-style composition.
- The control should be available where the user's thumb is already moving toward **Next**, so rating does not feel like an extra chore.

## Dock composition

- One floating, highly rounded panel with a white / very pale lavender, glass-like surface.
- Left:
  - circular soft-lavender medallion;
  - clean purple **brain / learning** outline icon;
  - thin vertical divider;
  - primary label: **Rate recall**;
  - muted secondary label: **Default: Good**.
- Right:
  - **Hard**
  - **Good**
  - **Easy**
- Rating buttons are clean text-only pills.
- **No arrows, faces, emojis, chevrons, or decorative symbols inside Hard / Good / Easy.**
- In the approved reference, **Good** is the selected state: rich brand-purple fill, white text.
- Hard and Easy remain light/white with restrained borders/shadows.
- Reuse existing project spacing, typography, colors, radii, and icon system wherever possible rather than copying mockup pixels literally.

## Ambient purple glow

The signature visual detail is a soft purple/lilac underglow around and underneath the floating dock.

Target feel:
- slightly stronger than an ordinary shadow, but still calm;
- premium ambient LED light behind a TV / under furniture;
- cozy and modern, **not** gamer-RGB or neon;
- softly diffused, with no hard luminous outline;
- visually related to the existing purple brand color.

Motion:
- the glow may drift slowly around the dock/perimeter;
- no flashing, fast pulsing, or distracting brightness changes;
- prefer GPU-friendly `transform` / `opacity` animation over layout- or paint-heavy animation;
- respect reduced-motion preferences; a static soft glow is acceptable when motion is reduced;
- the decorative glow layer must never intercept taps/pointer events.

## Interaction and FSRS behavior

This visual reference does **not** redefine FSRS scheduling semantics.

Preserve the currently implemented:
- FSRS scheduler and card state;
- rating/default/mapping behavior;
- migration and due-date preservation;
- undo/audit behavior;
- persistence and synchronization behavior;
- Next-button handling of the currently selected/default rating.

Do not add or remove a scheduler rating state merely because the mockup visually shows Hard / Good / Easy. Existing application behavior remains authoritative.

## Explicit non-scope

Do **not** redesign or restyle:
- question typography/layout;
- answer cards;
- Key Takeaway;
- source explanation;
- header/progress;
- Previous / Next buttons;
- FSRS data model/scheduler;
- whole-app navigation.

## Acceptance checklist

- Visually close to the sibling JPG on a narrow Android phone viewport.
- Brain medallion is present and visually balanced.
- Hard / Good / Easy are clean, text-only controls.
- Selected state is immediately obvious without extra symbols.
- Purple ambient glow is moderately visible, soft, premium, and non-distracting.
- No clipping/overflow on narrow phones.
- Glow never blocks interaction.
- Reduced-motion fallback works.
- Existing FSRS tests/contracts remain green.
- No unrelated question-screen changes.

## Agent handoff

A terminal coding agent should start with:

> Read `AGENTS.md` and `.project-memory/STATE.md` first. Then inspect `docs/ui-reference/fsrs-recall-dock-target.jpg` and read this specification. Treat them as the approved visual contract. Implement only this recall-dock UI refinement; preserve existing FSRS behavior and all surrounding question UI.
