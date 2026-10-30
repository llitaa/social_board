# Graphics: errors seen, criteria that follow (30.10.2026)

Errors Anton found in the first renders, each turned into a criterion the renderer and the checkers enforce.

| # | Error seen | Criterion |
|---|---|---|
| 1 | Text written over a line (line labels, "So läuft es wirklich") | No text touches a line or a shape it does not belong to. Line labels go into a legend, point labels are moved until free. |
| 2 | Dots on the curves (circle markers) | No dots, no markers, no decorative shapes. A point on a curve is named by its label only. |
| 3 | Tiny text under narrow blocks ("Anforderungen", 20 px) | No text under 26 px anywhere except the series tag. If a label does not fit, the layout changes, not the font. |
| 4 | Diamond gate touching the neighbouring boxes, arrows hidden behind it | No shape touches another shape: at least 24 px clear space between any two shapes; arrows are visible from end to end. |
| 5 | Legend colliding with the title | Title, legend, drawing and axis labels are separate bands with at least 30 px between them. |
| 6 | Label touching the axis ("Tal der Ausnahmen") | At least 24 px between any text and the axes or the canvas margin; nothing within 60 px of the canvas edge. |
| 7 | Two rows of blocks, lower third empty | The drawing uses the canvas: the drawing band spans from under the legend to 150 px above the bottom edge. |
| 8 | Name and role in the corner, a note line at the foot | Only: series tag, title, drawing. No name, no role, no caption inside the picture. |
| 9 | Colours outside the brand | AlpiType logo colours only (#0f3a50, #20B8D0, #01BC56, #00BEE6, #08E3FB, #BEF7FF) plus one grey for axes. |
| 10 | Too many words (lists as pictures) | At most 40 words in the picture, at most one title, at most 6 labels in the drawing. |
| 11 | Chart over-engineered (shaded areas, double labels, big arrowheads) | One visual idea per picture: lines, blocks or boxes, never all three; arrowheads small and thin. |

Automatic checker (pipeline/graphics.py, runs after every render): 1, 2, 3, 4, 6, 10 measured in the browser (bounding boxes, path sampling, font sizes, element count); 5, 7, 8, 9, 11 are layout rules in the templates. Two independent reviewers (Agent tool, each reads the PNGs cold with this table) judge what the numbers cannot: readability at phone size, whether the picture carries the point, anything that still looks generated.
