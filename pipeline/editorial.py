"""Editorial metadata per draft (F1, 31.10.2026): who specifically would care, the non-obvious observation, and what one could
agree or disagree with. Produced by the model together with the text, stored in the draft JSON, shown on the board. Not a gate:
a strong post without a debate hook is still allowed ("none"). Evidence stays in `signals` (lead and AI sentence)."""
EDITORIAL_PROMPT = """Editorial notes (one line each, German, not part of the post): reader = who specifically would care about this post (a role and a situation,
not an audience); insight = the non-obvious idea or practical observation the post carries; discussion_reason = what a reader could reasonably
agree or disagree with, or "none" if the post simply informs; situation = which problem situation the post tells from: "1" (a business
needs its own software solution and has nobody to build it), "2" (a company needs an additional application without using its product team),
or "beide". Confidentiality: clients of the last twelve months may only be described so that
sector plus place plus detail do not identify them; a made-up or composite scenario is marked as "Beispiel" in the text."""
EDITORIAL_JSON = ', "editorial": {"reader": "one line", "insight": "one line", "discussion_reason": "one line or none", "situation": "1 | 2 | beide"}'
