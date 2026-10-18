"""Animated segmented control — the Streamlit-native port of the reference
motion/react tabs component.

The React component can't run here (no React runtime in a Python Streamlit
app), so this ports the *behaviours* that make it feel good, one-for-one:

  - layoutId "selection"  -> a single accent pill that glides between
    triggers on a spring curve (direction is inherent: it travels the real
    distance, so it moves left when you pick an earlier tab and right for a
    later one, exactly like LayoutGroup).
  - panelMotion variants   -> the caller gets `direction` back so the panel
    below can enter/exit on the matching side.
  - roving focus + arrows  -> ArrowLeft/ArrowRight/Home/End move selection,
    one tab stop for the whole group (Radix's model).
  - TabsList overflow       -> if triggers overflow the viewport, lucide-style
    chevron scroll buttons appear and reveal the focused/active trigger.
  - useReducedMotion        -> prefers-reduced-motion collapses every spring
    to an instant jump.

The browser owns a persistent DOM and hands the value back via a component
value, so the glide plays *before* Streamlit reruns. Doing this with st.radio
is impossible — Streamlit 1.29 rebuilds the widget DOM on every change, so a
CSS transition has no same-node to animate and the pill snaps.
"""
import json

import streamlit.components.v1 as components

import app_theme


def render(options, active, on_key="seg", kind="methods", compact=False):
    """Render the animated segmented control and return the selected option.

    options  list[str]  trigger labels, in order
    active   str        currently selected label (must be in options)
    on_key   str        component key — keep one per control on the page
    kind     str        "methods" | "theme" — selects aria-label + height
    compact  bool       tighter padding (theme toggle in the top bar)
    """
    if active not in options:
        active = options[0]

    label = {
        "methods": "Pricing method",
        "theme": "Color theme",
    }.get(kind, "Options")

    # The pill glides to the clicked trigger, THEN we report the value. The
    # component value triggers the rerun; by then the glide has played, so the
    # page returns with the pill already parked on the new trigger.
    payload = {
        "options": options,
        "active": options.index(active),
        "onKey": on_key,
        "label": label,
        "compact": bool(compact),
        "colors": {
            "accent": _c("accent"),
            "onAccent": _c("onAccent"),
            "raised": _c("raised"),
            "surface": _c("surface"),
            "text": _c("text"),
            "text2": _c("text2"),
            "border": _c("border"),
        },
    }

    components.html(_HTML.replace("__PAYLOAD__", json.dumps(payload)),
                    height=46 if compact else 54)


def _c(name):
    theme = app_theme.current()
    palette = app_theme.DARK if theme == "dark" else app_theme.LIGHT
    return palette[name]


_HTML = r"""
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  :root {
    --spring-morph: cubic-bezier(.34, 1.32, .42, 1);  /* motionTokens.spring.morph */
    --spring-smooth: cubic-bezier(.22, 1, .36, 1);    /* motionTokens.spring.smooth */
    --ease-standard: cubic-bezier(.22, 1, .36, 1);
    --dur-fast: 160ms;
    --dur-morph: 420ms;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: transparent; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  }
  .shell { position: relative; width: 100%; }
  .viewport { overflow: hidden; border-radius: 999px; }
  .list {
    position: relative; display: flex; gap: 4px;
    background: var(--raised); border: 1px solid var(--border);
    border-radius: 999px; padding: 4px;
  }
  .compact .list { padding: 3px; gap: 2px; }

  /* layoutId "selection": one pill, transformed into place */
  .pill {
    position: absolute; top: 4px; left: 4px; bottom: 4px;
    border-radius: 999px; background: var(--accent); z-index: 0;
    transition: transform var(--dur-morph) var(--spring-morph),
                width  var(--dur-morph) var(--spring-morph);
    will-change: transform, width;
  }
  .compact .pill { top: 3px; left: 3px; bottom: 3px; }

  .trigger {
    position: relative; z-index: 1; flex: 1 1 0;
    appearance: none; border: 0; background: transparent; cursor: pointer;
    padding: 11px 16px; border-radius: 999px;
    font: inherit; font-weight: 600; font-size: .92rem; white-space: nowrap;
    color: var(--text2); transition: color var(--dur-fast) var(--ease-standard);
  }
  .compact .trigger { padding: 8px 15px; font-size: .84rem; }
  .trigger:hover:not([aria-checked="true"]) { color: var(--text); }
  .trigger[aria-checked="true"] { color: var(--onAccent); }
  .trigger:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

  /* TabsList overflow arrows (lucide ChevronLeft/Right) */
  .scrollBtn {
    position: absolute; top: 4px; bottom: 4px; width: 30px; z-index: 3;
    display: none; align-items: center; justify-content: center;
    border: 0; cursor: pointer; color: var(--text);
    background: linear-gradient(90deg, var(--raised), transparent);
  }
  .scrollBtn.right { right: 0; background: linear-gradient(270deg, var(--raised), transparent); }
  .scrollBtn.left  { left: 0; }
  .shell[data-overflow="true"] .scrollBtn { display: flex; }
  .shell[data-overflow="true"] .viewport { padding: 0 30px; }
  .scrollBtn[disabled] { opacity: 0; pointer-events: none; }

  @media (prefers-reduced-motion: reduce) {
    .pill { transition: none; }
  }
</style></head>
<body>
  <div class="shell" id="shell" data-overflow="false">
    <button class="scrollBtn left" id="btnL" aria-label="Scroll tabs left" disabled>
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
           aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
    </button>
    <div class="viewport" id="viewport">
      <div class="list" id="list" role="radiogroup">
        <span class="pill" id="pill" aria-hidden="true"></span>
      </div>
    </div>
    <button class="scrollBtn right" id="btnR" aria-label="Scroll tabs right" disabled>
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
           aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
    </button>
  </div>

<script>
(function () {
  const D = __PAYLOAD__;
  const list = document.getElementById('list');
  const pill = document.getElementById('pill');
  const shell = document.getElementById('shell');
  const viewport = document.getElementById('viewport');
  if (D.compact) shell.classList.add('compact');

  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const triggers = [];

  D.options.forEach((label, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'trigger';
    b.setAttribute('role', 'radio');
    b.setAttribute('data-value', label);
    b.setAttribute('aria-checked', i === D.active ? 'true' : 'false');
    b.tabIndex = i === D.active ? 0 : -1;          // roving tabindex
    b.textContent = label;
    b.addEventListener('click', () => select(i, true, true));
    list.appendChild(b);
    triggers.push(b);
  });

  let current = D.active;

  // Move the layoutId pill. animate=false paints the entrance instantly.
  function place(i, animate) {
    const t = triggers[i];
    if (!animate || reduced) pill.style.transition = 'none';
    pill.style.width = t.offsetWidth + 'px';
    pill.style.transform = 'translateX(' + (t.offsetLeft - 4) + 'px)';
    if (!animate || reduced) { pill.offsetHeight; pill.style.transition = ''; }
  }

  // report(direction) so the panel below can enter/exit on the matching side.
  function select(i, animate, report) {
    if (i < 0 || i >= triggers.length || i === current) { if (report) commit(i); return; }
    const dir = i > current ? 1 : -1;
    triggers.forEach((t, j) => {
      t.setAttribute('aria-checked', j === i ? 'true' : 'false');
      t.tabIndex = j === i ? 0 : -1;
    });
    current = i;
    place(i, animate);
    reveal(triggers[i]);
    if (report) commit(i, dir);
  }

  function commit(i, dir) {
    window.parent.postMessage({
      type: 'streamlit:setComponentValue',
      value: D.options[i],
      dataType: 'json',
    }, '*');
  }

  // --- roving focus + keyboard (Radix model): one tab stop for the group
  list.addEventListener('keydown', (e) => {
    const k = e.key;
    let next = null;
    if (k === 'ArrowRight') next = (current + 1) % triggers.length;
    else if (k === 'ArrowLeft') next = (current - 1 + triggers.length) % triggers.length;
    else if (k === 'Home') next = 0;
    else if (k === 'End') next = triggers.length - 1;
    if (next === null) return;
    e.preventDefault();
    select(next, true, true);
    triggers[next].focus();
  });

  // --- TabsList overflow: reveal the focused/active trigger inside the viewport
  function reveal(el) {
    if (shell.dataset.overflow !== 'true' || !el) return;
    const frame = viewport.getBoundingClientRect();
    const item = el.getBoundingClientRect();
    const max = Math.max(0, viewport.scrollWidth - viewport.clientWidth);
    const left = frame.left + (viewport.scrollLeft > 1 ? 30 : 0);
    const right = frame.right - (viewport.scrollLeft < max - 1 ? 30 : 0);
    const delta = item.left < left ? item.left - left
               : item.right > right ? item.right - right : 0;
    if (delta) viewport.scrollBy({ left: delta, behavior: reduced ? 'instant' : 'smooth' });
  }

  const btnL = document.getElementById('btnL');
  const btnR = document.getElementById('btnR');
  function updateEdges() {
    const max = Math.max(0, viewport.scrollWidth - viewport.clientWidth);
    shell.dataset.overflow = String(viewport.scrollWidth > shell.clientWidth + 1);
    btnL.disabled = viewport.scrollLeft <= 1;
    btnR.disabled = viewport.scrollLeft >= max - 1;
  }
  btnL.addEventListener('click', () =>
    viewport.scrollBy({ left: -viewport.clientWidth * 0.75, behavior: reduced ? 'instant' : 'smooth' }));
  btnR.addEventListener('click', () =>
    viewport.scrollBy({ left: viewport.clientWidth * 0.75, behavior: reduced ? 'instant' : 'smooth' }));
  viewport.addEventListener('scroll', updateEdges, { passive: true });
  list.addEventListener('focusin', (e) => reveal(e.target));
  new ResizeObserver(updateEdges).observe(list);

  // --- paint the entrance without animating, then settle edges
  requestAnimationFrame(() => {
    place(current, false);
    reveal(triggers[current]);
    updateEdges();
  });
})();
</script>
</body></html>
"""
