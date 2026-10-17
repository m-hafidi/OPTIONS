# Design

<!-- impeccable:design-schema 1 -->

## World: Airbnb-dark

A booking-app calm applied to a finance tool. Borrow the *structural* grammar of modern consumer product UI (Airbnb, Uber) — not its photography, not its travel content. One idea on screen at a time, enormous breathing room, a single saturated accent that only ever means "this is the action / this is the value." Dark-first because the user asked for it; light is a genuine second theme, not an afterthought.

### Color strategy

Restrained. A near-black neutral canvas plus exactly one accent. The accent carries meaning and never decorates.

**Dark theme (default)**
- Canvas `#0A0A0B` — page ground
- Surface `#141416` — cards
- Surface-raised `#1E1E21` — inputs, inactive controls
- Border `#2A2A2E` — hairlines
- Text-primary `#F5F5F7` — headings, values
- Text-secondary `#A1A1A6` — labels, captions
- Accent `#FF385C` — the "Rausch" pink-red. Primary button, active segment, focused input, price figure, slider fill.

**Light theme**
- Canvas `#FFFFFF`
- Surface `#FFFFFF`
- Surface-raised `#F4F4F5` — inputs, inactive controls
- Border `#E6E6E9`
- Text-primary `#141416`
- Text-secondary `#6B6B73`
- Accent `#E11D48` — darkened for contrast on white.

Rule: accent appears on at most three things per view — the primary action, the selected segment, the result figure. Everything else is neutral.

### Typography

System-native geometric sans — the family the reference product UIs ship with. Stack: `-apple-system, "Segoe UI", system-ui, sans-serif`. No webfont; it keeps the tool fast and honest.

- Display / result figure: 48–64px, weight 800, tight tracking (`-0.03em`)
- Page title: 28–32px, weight 700
- Card / section label: 13px, weight 600, uppercase, tracked `+0.08em`, text-secondary
- Body / control label: 15px, weight 500
- Caption: 13px, weight 400, text-secondary

Numbers use tabular figures so the price doesn't jitter between runs.

### Shape & spacing

- Radius: controls `12px`, cards `20px`, pills (segments, primary button) fully rounded.
- One spacing rhythm, base 8. Card padding `24–32px`. Gap between a label and its control `8px`; between stacked groups `24px`.
- Cards are flat: 1px border, no heavy shadow in dark. Light theme may use a single soft shadow `0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.04)`.
- More space above a heading than below it.

### Composition

Single centered column, max-width ~720px, generous vertical rhythm. No sidebar. Order: page title → segmented model switcher (a pill group, full width) → one parameter card (ticker, strike, rate, volatility, expiry, model-specific knob) → full-width accent "Calculate" pill → result band with the oversized call/put figures → the proof chart on the surface card.

The first viewport must already show the switcher and the parameter card — the task starts immediately, no hero.

### Controls

- Segmented switcher: pill group on surface-raised; active pill = accent background, white text; inactive = text-secondary, hover lifts to surface.
- Inputs: surface-raised ground, 1px border, accent border on focus, no inner shadow. Slider track fills accent up to the thumb.
- Primary button: full-width pill, accent ground, white text, weight 700. Hover deepens accent + lifts 1px; active scales 0.99. It is the only filled button on the screen.
- Theme toggle: small ghost icon-pill top-right (sun/moon), text-secondary, accent on hover.

### Motion

Purposeful and short (150–200ms), ease-out. Hover/focus on controls, the button press, the result figure fading up when a price lands, chart redraw. No looping decoration, no parallax.

### Data graphics

Charts are proof, not ornament. Render on the surface card with the theme's text color for axis labels/ticks, border-colored gridlines (or none), and an accent line for the price series. Transparent figure background so it sits on the card.

### Accessibility

Contrast holds in both themes (accent darkened in light). Every control keeps its native label. The selected segment is signaled by fill + weight, not color alone. Focus is always visible. Results readable without color.

### Never

- No travel imagery, no photography, no gradient meshes, no glassmorphism, no neon glow.
- No more than one accent hue on screen.
- No dense tables, no sidebars, no dashboard-of-many-charts.
- No default blue Streamlit widgets left unthemed.
