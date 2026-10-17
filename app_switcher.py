"""Animated segmented model switcher.

This is the Streamlit-native answer to the reference motion/react tabs: the
browser owns a persistent DOM with a highlight that glides between segments,
and it hands the chosen value back to Python via a query param. Doing this
with st.radio is impossible — Streamlit 1.29 rebuilds the widget DOM on every
change, so a CSS transition has no same-node to animate and the highlight
snaps instead of gliding. Owning the DOM is what lets the glide exist.
"""
import streamlit as st
import streamlit.components.v1 as components


def _token(p, name):
    """Pull a design token from app_theme so the switcher matches the page."""
    return p[name]


def render(options, active, on_key="model", colors=None):
    """Render the animated switcher and return the selected option.

    options     list[str]  segment labels, in order
    active      str        currently selected label (must be in options)
    on_key      str        query-param name used to hand the value back
    colors      dict       design tokens (defaults to the active theme)
    """
    if colors is None:
        colors = app_theme_colors()

    # The highlight glides to the clicked segment, THEN we report the value.
    # Setting the query param reruns the script; by then the glide has played,
    # so the page comes back with the highlight already parked on the new pill.
    js_options = ", ".join(f'{{"label": {o!r}}}'.replace("'", '"') for o in options)
    active_idx = options.index(active) if active in options else 0

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  :root {{
    --accent: {colors['accent']};
    --on-accent: {colors['onAccent']};
    --raised: {colors['raised']};
    --text2: {colors['text2']};
    --text: {colors['text']};
    --border: {colors['border']};
    --spring: cubic-bezier(.34, 1.4, .5, 1);
    --fast: 160ms;
    --glide: 520ms;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  }}
  .seg {{
    position: relative; display: flex; gap: 4px;
    background: var(--raised); border: 1px solid var(--border);
    border-radius: 999px; padding: 4px; width: 100%;
  }}
  /* the single sliding highlight — the layoutId equivalent */
  .seg .pill {{
    position: absolute; top: 4px; left: 4px; bottom: 4px;
    border-radius: 999px; background: var(--accent);
    transition: transform var(--glide) var(--spring), width var(--glide) var(--spring);
    will-change: transform, width; z-index: 0;
  }}
  .seg button {{
    position: relative; z-index: 1; flex: 1 1 0;
    appearance: none; border: 0; background: transparent; cursor: pointer;
    padding: 10px 14px; border-radius: 999px;
    font: inherit; font-weight: 600; font-size: .9rem; white-space: nowrap;
    color: var(--text2);
    transition: color var(--fast) ease;
  }}
  .seg button:hover:not([aria-checked="true"]) {{ color: var(--text); }}
  .seg button[aria-checked="true"] {{ color: var(--on-accent); }}
  .seg button:focus-visible {{
    outline: 2px solid var(--accent); outline-offset: 3px;
  }}
  @media (prefers-reduced-motion: reduce) {{
    .seg .pill {{ transition: none; }}
  }}
</style>
</head>
<body>
  <div class="seg" id="seg" role="radiogroup" aria-label="Pricing model">
    <span class="pill" id="pill"></span>
  </div>

<script>
  const OPTIONS = {js_options_js};
  const ACTIVE = {active_idx};
  const ON_KEY = {on_key_js};
  const seg = document.getElementById('seg');
  const pill = document.getElementById('pill');
  const buttons = [];

  function place(btn, animate) {{
    if (!animate) pill.style.transition = 'none';
    pill.style.width = btn.offsetWidth + 'px';
    pill.style.transform = 'translateX(' + (btn.offsetLeft - 4) + 'px)';
    if (!animate) {{ pill.offsetHeight; pill.style.transition = ''; }}
  }}

  function select(i, animate) {{
    buttons.forEach((b, j) => b.setAttribute('aria-checked', j === i ? 'true' : 'false'));
    place(buttons[i], animate);
    // hand the value to Python; this reruns the script with the pill already moved
    const url = new URL(window.location);
    url.searchParams.set(ON_KEY, OPTIONS[i].label);
    window.parentStreamlit ? null : null;
    // Streamlit component value via query param — stable in 1.29
    window.parent.postMessage({{
      type: 'streamlit:setComponentValue',
      value: OPTIONS[i].label,
    }}, '*');
    // Fallback: also encode in the URL so a plain rerun keeps the choice
    try {{ window.parent.location.hash = ''; }} catch (e) {{}}
  }}

  OPTIONS.forEach((opt, i) => {{
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'radio');
    b.textContent = opt.label;
    b.addEventListener('click', () => select(i, true));
    seg.appendChild(b);
    buttons.push(b);
  }});

  // paint the initial position without animating the entrance
  requestAnimationFrame(() => select(ACTIVE, false));
</script>
</body>
</html>
    """

    # Inject the JS structures safely (quotes/braces handled above).
    html = html.replace("{js_options_js}", _js_array(options))
    html = html.replace("{on_key_js}", _js_str(on_key))

    components.html(html, height=52)


def app_theme_colors():
    import app_theme
    p = app_theme.DARK if app_theme.current() == "dark" else app_theme.LIGHT
    return p


def _js_array(options):
    inner = ",".join('{"label":' + _js_str(o) + "}" for o in options)
    return "[" + inner + "]"


def _js_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
