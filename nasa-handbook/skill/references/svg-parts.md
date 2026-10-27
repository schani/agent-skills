# SVG parts library

Copy-paste parts for handbook figures. Units are millimetres on paper: figures
use `viewBox="0 0 180 H"` and fill the 179 mm text column, so `H` is the
figure's height in mm. Classes and the `nh-*` markers come from
`assets/template.html`. The examples in `assets/examples/` use all of
these parts in context; search them for the part name.

Coordinates below are examples. Move them, but keep the sizes. When a part
must rise above the figure's first row (a breaker handle, a chart title),
start the viewBox at a negative y, `viewBox="0 -3.6 180 50"`, instead of
shifting everything down.

## Contents

- Structure: figure shell, box, panel, drum, bracket, figure code, detail inset
- Wiring: wire, arrow, junction, bus fan-out, wire label
- Period symbols: circuit breaker, selector switch, pushbutton, talkback, hex terminal, coil
- Drafting: callout and leader, dimensions, centerline, hidden line, section cut, section view, glass, axes
- Time and data: timeline axis and ticks, lanes and bars, events, markers, legend, sequence detail, parts strip
- Fluid and instruments: check valve, valve with actuator, pump, heat exchanger, gauge, sensor, station tags and station data, granular fill
- Charts: axes, ticks, axis titles, a computed curve, reference lines, marked points, process path

## Vector textures

Use explicit black strokes or circles for textures. For curved or irregular
faces, clip the vectors to a copy of the face in a uniquely named `clipPath`.
Keep vectors within the face's bounding box; clear them behind labels with a
paper-filled shape. Vector textures retain black/white source ink in Chrome's
PDF. The snippets below include their hatch strokes and stipple circles.

## Structure

Figure shell (caption and code included):

```html
<figure>
  <svg viewBox="0 0 180 66" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="What the figure shows">
    <!-- parts -->
    <text class="code" x="178.6" y="65.4" text-anchor="end">TLM-501A</text>
  </svg>
  <figcaption><span class="n">Figure 2.1-1.</span>Recording System Functional Diagram</figcaption>
</figure>
```

Box with a title and up to three detail lines (title 2.35, details 2.05, about
2.7 mm apart; centre the block vertically):

```html
<rect class="box" x="85" y="7" width="28" height="15"/>
<text class="lbl"   x="99" y="11"   text-anchor="middle">TELEMETRY ROUTER</text>
<text class="lbl-s" x="99" y="14.2" text-anchor="middle">SESSIONS, ROUTES</text>
<text class="lbl-s" x="99" y="16.8" text-anchor="middle">STATION CLOCK</text>
<text class="lbl-s" x="99" y="19.4" text-anchor="middle">ACCESS TOKENS (SIGNED)</text>
```

Width guide for Routed Gothic Narrow: about 1.2 mm per character at 2.35 and
1.05 mm at 2.05. Leave at least 1.5 mm between text and a box edge.

Dashed panel (a runtime, device or trust boundary) with its name inside, top left:

```html
<rect class="panel" x="1.5" y="2.5" width="77" height="64.5"/>
<text class="lbl-s" x="3.4" y="5.6">FIELD STATION (1 OF ≤ 8)</text>
```

Drum (storage: a database, bucket or disk). Body path, then the top ellipse
drawn over it:

```html
<path class="box" d="M120,31 L120,44.6 A8.5,1.8 0 0 0 137,44.6 L137,31"/>
<ellipse class="box" cx="128.5" cy="31" rx="8.5" ry="1.8"/>
<text class="lbl-b" x="128.5" y="36.6" text-anchor="middle">ARCHIVE</text>
<text class="lbl-s" x="128.5" y="39.4" text-anchor="middle">OBJECT STORE</text>
```

Bracket grouping a row of parts, with its label above:

```html
<polyline class="w" points="24,14.4 24,13.2 75,13.2 75,14.4"/>
<text class="lbl-s" x="49.5" y="12.2" text-anchor="middle">ENCODER CHAIN (ONE PER STATION)</text>
```

Detail inset on the right of a secondary figure, after a thin divider:

```html
<line class="t" x1="123.4" y1="-0.6" x2="123.4" y2="47.6"/>
<text class="lbl-b" x="126" y="2">DETAIL A: CLOCK SYNC</text>
```

## Wiring

```html
<line class="wa" x1="113" y1="35" x2="119.6" y2="35"/>            <!-- arrow; stop 0.4 short of the target edge -->
<polyline class="wa" points="75,55.4 79.8,55.4 79.8,35 84.6,35"/>   <!-- routed wire, right angles only -->
<line class="w" x1="22" y1="10.5" x2="42" y2="10.5"/>               <!-- plain wire -->
<circle class="dot" cx="42" cy="10.5" r="0.55"/>                    <!-- junction: wires join here -->
<text class="lbl-s" x="114" y="34.2">PART</text>                     <!-- wire name: 0.8 above the wire, near its start -->
<text class="lbl-s" transform="translate(82.1 52.6) rotate(-90)">4 MB BLOCKS</text>  <!-- on a vertical wire -->
```

Bus fan-out (one source feeding a column of boxes):

```html
<line class="w" x1="137" y1="37.5" x2="142.5" y2="37.5"/>
<line class="w" x1="142.5" y1="11.5" x2="142.5" y2="50.5"/>
<circle class="dot" cx="142.5" cy="37.5" r="0.5"/>
<line class="wa" x1="142.5" y1="11.5" x2="144.6" y2="11.5"/>
<line class="wa" x1="142.5" y1="24.5" x2="144.6" y2="24.5"/>
<!-- … one arrow per box … -->
```

Bus bar (power or data bus drawn as a narrow bar, label rotated beside it):

```html
<rect class="box" x="42" y="4" width="2" height="39.6"/>
<text class="lbl-s" transform="translate(40.9 23.6) rotate(-90)" text-anchor="middle">AGS BUS</text>
```

## Period symbols

Circuit breaker (two terminals, an arc and a pull handle), with name, rating and function:

```html
<line class="w" x1="22" y1="10.5" x2="28.6" y2="10.5"/>
<circle class="of" cx="29.2" cy="10.5" r="0.6"/><circle class="of" cx="33.8" cy="10.5" r="0.6"/>
<path class="w" d="M29.4,9.6 Q31.5,7.4 33.6,9.6"/>
<line class="w" x1="31.5" y1="8.1" x2="31.5" y2="6.6"/><line class="w" x1="30.4" y1="6.6" x2="32.6" y2="6.6"/>
<line class="w" x1="34.4" y1="10.5" x2="42" y2="10.5"/>
<text class="lbl-s" x="31.5" y="5.4"  text-anchor="middle">CB1</text>
<text class="lbl-s" x="31.5" y="13.2" text-anchor="middle">15A</text>
<text class="lbl-s" x="31.5" y="15.6" text-anchor="middle">AGS MAIN A</text>
```

Three-position selector (common terminal, lever to the selected contact):

```html
<circle class="of" cx="57.6" cy="18.6" r="0.6"/>
<line class="w" x1="58" y1="18.2" x2="64.5" y2="12.8"/>
<circle class="of" cx="65.2" cy="12.4" r="0.6"/>
<circle class="of" cx="65.6" cy="18.6" r="0.6"/>
<circle class="of" cx="65.2" cy="24.8" r="0.6"/>
<text class="lbl-s" x="64.6" y="10.8">A</text>
<text class="lbl-s" x="66.8" y="19.4">OFF</text>
<text class="lbl-s" x="64.6" y="27.8">B</text>
```

Momentary pushbutton (bar over two terminals, plunger above):

```html
<circle class="of" cx="54.6" cy="32" r="0.6"/><circle class="of" cx="59.4" cy="32" r="0.6"/>
<line class="w" x1="53.8" y1="29.8" x2="60.2" y2="29.8"/>
<line class="w" x1="57" y1="29.8" x2="57" y2="27.8"/><line class="w" x1="55.8" y1="27.8" x2="58.2" y2="27.8"/>
<text class="lbl-s" x="57" y="35.2" text-anchor="middle">S2 TRIGGER</text>
```

Talkback indicator, barber pole (striped = in transition, gray = ready):

```html
<defs><clipPath id="talkback-stripes"><circle cx="70" cy="43.6" r="2.2"/></clipPath></defs>
<path d="M72.2,41.4L72.2,41.4 M70.8,41.4L72.2,42.8 M69.4,41.4L72.2,44.2 M68,41.4L72.2,45.6 M71,45.8L67.8,42.6 M69.6,45.8L67.8,44 M68.2,45.8L67.8,45.4" fill="none" stroke="#000" stroke-width="0.7" clip-path="url(#talkback-stripes)"/>
<circle cx="70" cy="43.6" r="2.2" fill="none" stroke="#000" stroke-width="0.35"/>
<text class="lbl-s" x="73.4" y="43.4">AGS RDY TB</text>
<text class="lbl-s" x="73.4" y="45.8">GRAY = READY, BP = CHARGING</text>
```

Hex terminal (only when the text refers to the number):

```html
<g transform="translate(77 12.4)">
  <polygon class="of" points="-1.4,0 -0.7,-1.2 0.7,-1.2 1.4,0 0.7,1.2 -0.7,1.2"/>
  <text class="lbl-s" x="0" y="0.7" text-anchor="middle" style="font-size:1.8px">1</text>
</g>
```

Coil or inductor (four humps):

```html
<path class="w" d="M141,12 a1.4,1.4 0 0 1 2.8,0 a1.4,1.4 0 0 1 2.8,0 a1.4,1.4 0 0 1 2.8,0 a1.4,1.4 0 0 1 2.8,0"/>
```

## Drafting

Callout with leader. The label sits in a row above or below the object; the
leader starts just outside the text and ends on the part:

```html
<text class="lbl" x="84" y="5.2">SINGULARITY CORE</text>
<line class="ld" x1="90" y1="6.2" x2="88.8" y2="27.4"/>        <!-- label above: start 1 below the baseline -->
<text class="lbl" x="58.4" y="59.4">TRIGGER S2</text>
<line class="ld" x1="57.8" y1="58" x2="52.4" y2="45.6"/>        <!-- label below: start left of the text, above its cap line -->
```

Horizontal dimension: two extension lines, two half dimension lines with the
arrow at the extension end, and the value in the gap:

```html
<line class="t" x1="17" y1="39.6" x2="17" y2="66.4"/>
<line class="t" x1="130.6" y1="36" x2="130.6" y2="66.4"/>
<line class="dim" x1="17" y1="65.2" x2="63.6" y2="65.2"/>
<line class="dim" x1="130.6" y1="65.2" x2="83.6" y2="65.2"/>
<text class="lbl" x="65.2" y="66">27.60 [701]</text>
```

Vertical dimension (value reads bottom to top):

```html
<line class="t" x1="41" y1="15.4" x2="6.4" y2="15.4"/>
<line class="t" x1="31" y1="62.6" x2="6.4" y2="62.6"/>
<line class="dim" x1="8" y1="15.4" x2="8" y2="34.4"/>
<line class="dim" x1="8" y1="62.6" x2="8" y2="43.8"/>
<text class="lbl" transform="translate(8.9 43.4) rotate(-90)">9.25 [235]</text>
```

Centerline and hidden outline:

```html
<line class="cl" x1="12" y1="30" x2="141" y2="30"/>
<rect class="hid" x="25" y="23.4" width="15" height="8.6"/>
```

Section cut A–A (heavy dash-dot line, arrows show the viewing direction):

```html
<line class="cut" x1="103.9" y1="12.6" x2="103.9" y2="47.4"/>
<polyline class="w" points="103.9,12.6 107.6,12.6"/><path class="dot" d="M107.4,11.6 L109.4,12.6 L107.4,13.6 Z"/>
<polyline class="w" points="103.9,47.4 107.6,47.4"/><path class="dot" d="M107.4,46.4 L109.4,47.4 L107.4,48.4 Z"/>
<text class="lbl-b" x="110.4" y="13.5">A</text>
<text class="lbl-b" x="110.4" y="48.3">A</text>
```

Section view: hatched cut faces, crossing centerlines, title and scale below:

```html
<g transform="translate(160 29)">
  <defs><clipPath id="section-hatch"><circle r="13.4"/></clipPath></defs>
  <path d="M-12.95,-13.4L-13.4,-12.95 M-11.4,-13.4L-13.4,-11.4 M-9.85,-13.4L-13.4,-9.85 M-8.3,-13.4L-13.4,-8.3 M-6.75,-13.4L-13.4,-6.75 M-5.2,-13.4L-13.4,-5.2 M-3.65,-13.4L-13.4,-3.65 M-2.1,-13.4L-13.4,-2.1 M-0.55,-13.4L-13.4,-0.55 M1,-13.4L-13.4,1 M2.55,-13.4L-13.4,2.55 M4.1,-13.4L-13.4,4.1 M5.65,-13.4L-13.4,5.65 M7.2,-13.4L-13.4,7.2 M8.75,-13.4L-13.4,8.75 M10.3,-13.4L-13.4,10.3 M11.85,-13.4L-13.4,11.85 M13.4,-13.4L-13.4,13.4 M-11.85,13.4L13.4,-11.85 M-10.3,13.4L13.4,-10.3 M-8.75,13.4L13.4,-8.75 M-7.2,13.4L13.4,-7.2 M-5.65,13.4L13.4,-5.65 M-4.1,13.4L13.4,-4.1 M-2.55,13.4L13.4,-2.55 M-1,13.4L13.4,-1 M0.55,13.4L13.4,0.55 M2.1,13.4L13.4,2.1 M3.65,13.4L13.4,3.65 M5.2,13.4L13.4,5.2 M6.75,13.4L13.4,6.75 M8.3,13.4L13.4,8.3 M9.85,13.4L13.4,9.85 M11.4,13.4L13.4,11.4 M12.95,13.4L13.4,12.95" fill="none" stroke="#000" stroke-width="0.2" clip-path="url(#section-hatch)"/>
  <circle r="10.6" class="of"/>
  <circle r="13.4" class="o"/>
  <line class="cl" x1="-16.4" y1="0" x2="16.4" y2="0"/>
  <line class="cl" x1="0" y1="-16.4" x2="0" y2="16.4"/>
</g>
<text class="lbl-b" x="160" y="49.6" text-anchor="middle">SECTION A–A</text>
<text class="lbl-s" x="160" y="52.4" text-anchor="middle">LOOKING FWD, SCALE 1/2</text>
```

Glass (short parallel diagonal strokes in two corners of the pane):

```html
<g class="t"><line x1="80.6" y1="21.4" x2="83" y2="19.2"/><line x1="81.6" y1="22.4" x2="84.6" y2="19.6"/></g>
```

Coordinate axes (Y out of the page drawn as a dotted circle):

```html
<g transform="translate(150 63.6)">
  <line class="wa" x1="0" y1="0" x2="8.4" y2="0"/>
  <line class="wa" x1="0" y1="0" x2="0" y2="-5.6"/>
  <circle r="0.9" class="of"/><circle r="0.28" class="dot"/>
  <text class="lbl-s" x="9.2" y="0.8">+X</text>
  <text class="lbl-s" x="-1.2" y="-6.4">+Z</text>
  <text class="lbl-s" x="-4.8" y="2.8">+Y</text>
</g>
```

## Time and data

Timeline axis. Pick a scale (here x = 40 + 1.4 × seconds), majors every 10
with labels above, minors every 2. Generate the ticks rather than typing them:

```html
<text class="lbl-s" x="2" y="7.4">MISSION CLOCK, SEC</text>
<line class="w" x1="33" y1="8.2" x2="118" y2="8.2"/>
<g class="t" id="ticks"></g>
<g class="lbl-s" id="tick-labels" text-anchor="middle"></g>
<script>
  // x0: x at t=0; k: mm per unit; from/to: range in units
  ;(function (x0, k, from, to) {
    const ns = 'http://www.w3.org/2000/svg', ticks = document.getElementById('ticks'), labels = document.getElementById('tick-labels')
    for (let t = from; t <= to; t += 2) {
      const x = x0 + k * t, major = t % 10 === 0, l = document.createElementNS(ns, 'line')
      l.setAttribute('x1', x); l.setAttribute('x2', x); l.setAttribute('y1', 8.2); l.setAttribute('y2', major ? 6.8 : 7.6); ticks.append(l)
      if (major) { const s = document.createElementNS(ns, 'text'); s.setAttribute('x', x); s.setAttribute('y', 6); s.textContent = t; labels.append(s) }
    }
  })(40, 1.4, -2, 54)
</script>
```

Lanes: label column at x 2–30, bars 2.6 mm tall, lanes 4.4 mm apart. A break
in a bar is a new file or segment; `.gap` is a pending or absent span:

```html
<text class="lbl-s" x="2" y="21">STATION 2 · CAMERA</text>
<rect class="vid" x="40"   y="19.1" width="29.4" height="2.6"/>
<path d="M41.35,19.1L40,20.45 M42.9,19.1L40.3,21.7 M44.45,19.1L41.85,21.7 M46,19.1L43.4,21.7 M47.55,19.1L44.95,21.7 M49.1,19.1L46.5,21.7 M50.65,19.1L48.05,21.7 M52.2,19.1L49.6,21.7 M53.75,19.1L51.15,21.7 M55.3,19.1L52.7,21.7 M56.85,19.1L54.25,21.7 M58.4,19.1L55.8,21.7 M59.95,19.1L57.35,21.7 M61.5,19.1L58.9,21.7 M63.05,19.1L60.45,21.7 M64.6,19.1L62,21.7 M66.15,19.1L63.55,21.7 M67.7,19.1L65.1,21.7 M69.25,19.1L66.65,21.7 M68.2,21.7L69.4,20.5" fill="none" stroke="#000" stroke-width="0.2"/>
<rect class="vid" x="70.2" y="19.1" width="37"   height="2.6"/>
<path d="M70.8,19.1L70.2,19.7 M72.35,19.1L70.2,21.25 M73.9,19.1L71.3,21.7 M75.45,19.1L72.85,21.7 M77,19.1L74.4,21.7 M78.55,19.1L75.95,21.7 M80.1,19.1L77.5,21.7 M81.65,19.1L79.05,21.7 M83.2,19.1L80.6,21.7 M84.75,19.1L82.15,21.7 M86.3,19.1L83.7,21.7 M87.85,19.1L85.25,21.7 M89.4,19.1L86.8,21.7 M90.95,19.1L88.35,21.7 M92.5,19.1L89.9,21.7 M94.05,19.1L91.45,21.7 M95.6,19.1L93,21.7 M97.15,19.1L94.55,21.7 M98.7,19.1L96.1,21.7 M100.25,19.1L97.65,21.7 M101.8,19.1L99.2,21.7 M103.35,19.1L100.75,21.7 M104.9,19.1L102.3,21.7 M106.45,19.1L103.85,21.7 M105.4,21.7L107.2,19.9 M106.95,21.7L107.2,21.45" fill="none" stroke="#000" stroke-width="0.2"/>
<rect class="aud" x="40"   y="23.5" width="33.6" height="2.6"/>
<rect class="gap" x="73.6" y="23.5" width="9.8"  height="2.6"/>
```

Event (dashed vertical through all lanes, label on top) and marker triangle:

```html
<line class="ev" x1="107.2" y1="1.6" x2="107.2" y2="37.6"/>
<text class="lbl-s" x="107.2" y="1.2" text-anchor="middle">STOP</text>
<path class="dot" d="M58.9,7.4 L60.3,7.4 L59.6,8.6 Z"/>
<text class="lbl-s" x="59.6" y="6" text-anchor="middle">M</text>
```

Legend (bottom left, a swatch and a name per row):

```html
<rect class="vid" x="2" y="38.6" width="5" height="2.4"/>
<path d="M3.25,38.6L2,39.85 M4.8,38.6L2.4,41 M6.35,38.6L3.95,41 M5.5,41L7,39.5" fill="none" stroke="#000" stroke-width="0.2"/><text class="lbl-s" x="8.2" y="40.6">VIDEO STREAM</text>
<rect class="aud" x="2" y="42.4" width="5" height="2.4"/><text class="lbl-s" x="8.2" y="44.4">AUDIO STREAM</text>
```

Sequence detail (two lifelines, a request and a reply):

```html
<text class="lbl-s" x="133" y="6.4" text-anchor="middle">STATION</text>
<text class="lbl-s" x="169" y="6.4" text-anchor="middle">ROUTER</text>
<line class="w" x1="133" y1="7.4" x2="133" y2="23.4"/>
<line class="w" x1="169" y1="7.4" x2="169" y2="23.4"/>
<line class="wa" x1="133" y1="10" x2="168.6" y2="14.6"/>
<line class="wa" x1="169" y1="14.8" x2="133.4" y2="20.2"/>
<text class="lbl-s" x="151" y="11.2" text-anchor="middle">PING</text>
<text class="lbl-s" x="151" y="19.8" text-anchor="middle">PONG</text>
<text class="lbl-s" x="151" y="27" text-anchor="middle">OFFSET = SERVER − (T0 + T1) / 2</text>
```

Parts strip (a file cut into fixed parts; hatched = special, dotted = filling):

```html
<rect class="vid" x="126" y="36.6" width="8" height="3.6"/>
<path d="M126.15,36.6L126,36.75 M127.7,36.6L126,38.3 M129.25,36.6L126,39.85 M130.8,36.6L127.2,40.2 M132.35,36.6L128.75,40.2 M133.9,36.6L130.3,40.2 M131.85,40.2L134,38.05 M133.4,40.2L134,39.6" fill="none" stroke="#000" stroke-width="0.2"/>
<rect class="aud" x="134" y="36.6" width="8" height="3.6"/>
<rect class="gap" x="158" y="36.6" width="8" height="3.6"/>
<rect x="129.2" y="37.3" width="1.6" height="2.2" style="fill: var(--paper)"/>  <!-- clears the hatch behind a digit -->
<text class="lbl-s" x="130" y="39.2" text-anchor="middle">1</text>
```

## Fluid and instruments

Flow lines are `.w` / `.wa` wires; arrows show flow direction. These parts sit
on a line and break it.

Check valve (flow left to right; the bar is the seat):

```html
<line class="w" x1="19" y1="23" x2="23.4" y2="23"/>
<path class="of" d="M23.4,21.6 L23.4,24.4 L25.8,23 Z"/>
<line class="w" x1="26" y1="21.6" x2="26" y2="24.4"/>
<text class="lbl-s" x="24.7" y="20.6" text-anchor="middle">V1</text>
```

Two-way valve with actuator (bow tie, stem, actuator box):

```html
<path class="of" d="M18.8,35.6 L18.8,38.4 L21,37 Z"/>
<path class="of" d="M23.2,35.6 L23.2,38.4 L21,37 Z"/>
<line class="w" x1="21" y1="37" x2="21" y2="33.6"/>
<rect class="box" x="19.2" y="31.2" width="3.6" height="2.4"/>
<text class="lbl-s" x="21" y="30" text-anchor="middle">BPV-2</text>
```

Pump (circle with a filled triangle pointing downstream):

```html
<circle class="of" cx="63" cy="23" r="2.6"/>
<path class="dot" d="M61.8,21.6 L64.8,23 L61.8,24.4 Z"/>
<text class="lbl-s" x="63" y="28.2" text-anchor="middle">P1 PUMP</text>
```

Heat exchanger (a box with the two passes drawn as opposed thin arrows):

```html
<rect class="box" x="34" y="19" width="22" height="22"/>
<line class="ld" x1="35" y1="23" x2="55" y2="23"/>
<line class="ld" x1="55" y1="37" x2="35" y2="37"/>
<text class="lbl-b" x="45" y="28.6" text-anchor="middle">HX1</text>
<text class="lbl" x="45" y="31.4" text-anchor="middle">EXTRACT COOLER</text>
```

Gauge on a tee (junction dot, stem, dial with a needle):

```html
<circle class="dot" cx="95.4" cy="13" r="0.5"/>
<line class="w" x1="95.4" y1="13" x2="95.4" y2="17.4"/>
<circle class="of" cx="95.4" cy="19" r="1.6"/>
<line class="w" x1="95.4" y1="19" x2="96.4" y2="17.9"/>
<text class="lbl-s" x="95.1" y="23" text-anchor="middle">BREW PRESS</text>
```

Sensor (tagged circle on a stem; a dashed `.ev` line carries its signal to
what it controls). Make the circle big enough for its tag: r 1.7 for two
characters at 1.8 px:

```html
<line class="w" x1="27.8" y1="37" x2="27.8" y2="33.9"/>
<circle class="of" cx="27.8" cy="32.2" r="1.7"/>
<text class="lbl-s" x="27.8" y="32.85" text-anchor="middle" style="font-size:1.8px">T2</text>
<line class="ev" x1="26.1" y1="32.2" x2="22.8" y2="32.2"/>
```

Station tags (numbered circles on the lines) and a station data list keyed to
them. Use them when the text or a chart refers to points in the flow:

```html
<g transform="translate(58.2 23)"><circle class="of" r="1.3"/><text class="lbl-s" y="0.65" text-anchor="middle" style="font-size:1.8px">2</text></g>

<text class="lbl-s" x="35" y="43.6">STATION DATA:</text>
<text class="lbl-s" x="35" y="46">PRESSURE ABS, TEMP</text>
<g transform="translate(59.4 40.9)"><circle class="of" r="1.3"/><text class="lbl-s" y="0.65" text-anchor="middle" style="font-size:1.8px">1</text><text class="lbl-s" x="2" y="0.75">2.4 BAR, 22 °C</text></g>
```

Granular or packed material (grounds, powder, pellets, a filter bed): use
explicit stipple circles inside a `.grain` outline. Clear dots behind a label
with a paper rectangle, as the parts strip does for its digits:

```html
<rect class="grain" x="102" y="15.4" width="16" height="3.2"/>
<g class="dot">
  <circle cx="102.6" cy="16.2" r="0.15"/><circle cx="103.9" cy="16.2" r="0.15"/><circle cx="105.2" cy="16.2" r="0.15"/><circle cx="106.5" cy="16.2" r="0.15"/>
  <circle cx="107.8" cy="16.2" r="0.15"/><circle cx="109.1" cy="16.2" r="0.15"/><circle cx="110.4" cy="16.2" r="0.15"/><circle cx="111.7" cy="16.2" r="0.15"/>
  <circle cx="113" cy="16.2" r="0.15"/><circle cx="114.3" cy="16.2" r="0.15"/><circle cx="115.6" cy="16.2" r="0.15"/><circle cx="116.9" cy="16.2" r="0.15"/>
  <circle cx="103" cy="17.5" r="0.15"/><circle cx="104.3" cy="17.5" r="0.15"/><circle cx="105.6" cy="17.5" r="0.15"/><circle cx="106.9" cy="17.5" r="0.15"/>
  <circle cx="108.2" cy="17.5" r="0.15"/><circle cx="109.5" cy="17.5" r="0.15"/><circle cx="110.8" cy="17.5" r="0.15"/><circle cx="112.1" cy="17.5" r="0.15"/>
  <circle cx="113.4" cy="17.5" r="0.15"/><circle cx="114.7" cy="17.5" r="0.15"/><circle cx="116" cy="17.5" r="0.15"/><circle cx="117.3" cy="17.5" r="0.15"/>
</g>
```

## Charts

A chart is a DETAIL inset or a whole secondary figure: L-shaped axes, short
ticks (1.2 major, 0.8 minor), tick labels in `.lbl-s`, axis titles with
units, the y title rotated. Compute the curve's points in a script and paste
them as one polyline, two decimals each. Reference levels and limits are
dashed `.ev` lines labelled on the line.

```html
<!-- x: 40..100 kPa over 139..176; y: 70..100 °C over 33..3 -->
<polyline class="w" points="139,3 139,33 176,33"/>
<g class="t">
  <line x1="139" y1="33" x2="139" y2="34.2"/><line x1="149.57" y1="33" x2="149.57" y2="34.2"/>
  <line x1="139" y1="23" x2="137.8" y2="23"/><line x1="139" y1="13" x2="137.8" y2="13"/>
</g>
<g class="lbl-s" text-anchor="middle"><text x="139" y="36.4">40</text><text x="149.57" y="36.4">60</text></g>
<g class="lbl-s" text-anchor="end"><text x="137.4" y="23.7">80</text><text x="137.4" y="13.7">90</text></g>
<text class="lbl-s" x="157.5" y="39.4" text-anchor="middle">PRESSURE, KPA ABS</text>
<text class="lbl-s" transform="translate(131.4 18) rotate(-90)" text-anchor="middle">TEMPERATURE, °C</text>
<polyline class="w" points="139.00,27.06 144.29,21.61 149.57,17.01 154.86,13.01 160.14,9.47 165.43,6.28 170.71,3.37"/>
<line class="ev" x1="139" y1="23" x2="171.41" y2="23"/>
<text class="lbl-s" x="156" y="22.2" text-anchor="middle">T2 LIMIT 80 °C</text>
<circle class="dot" cx="147.72" cy="18.54" r="0.5"/>                       <!-- a marked point -->
<g class="w"><line x1="146.82" y1="9.1" x2="148.62" y2="10.9"/><line x1="146.82" y1="10.9" x2="148.62" y2="9.1"/></g>  <!-- an X: a state to avoid -->
<line class="wa" x1="171.41" y1="16.4" x2="171.41" y2="25.4"/>             <!-- process path between stations -->
```
