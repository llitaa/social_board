# strategy/ — Positionierung, Zielgruppen, Lessons Learned

Die eine Stelle für Strategie-Dokumente. Firmenfakten bleiben in `~/.claude/alpitype/company-context.md`; der Draft-Prompt liest `library/positioning.md`, das aus `05-positionierung-vN` abgeleitet wird, nie umgekehrt.

| Datei | Was | Von |
|---|---|---|
| `01-grundlagen-2026-11-01.md` | Was steht fest (Ziel, Positionierung, Zielgruppen A/B, Learning, 18 Monate Akquise) mit Prüfvermerk | zweiter Agent, Prüfvermerk Claude |
| `02-lessons-learned-2026-11-01.md` | Fälle, Fehlerhypothesen, was nicht bewiesen ist, Prüffragen; mit Prüfvermerk | zweiter Agent, Prüfvermerk Claude |
| `03-offene-fragen-2026-11-01.md` | Sieben Fragenkomplexe zu Kundenprofilen | zweiter Agent |
| `04-kundenprofile-2026-11-01.md` | Antwort: Urteil, drei Profile, acht Probleme, zwei Kritiker, Empfehlung, Unsicherheiten | Claude |
| `05-positionierung-v1-2026-11-01.md` | Zusammenführung: drei Sätze, drei Adressaten, Angebote, Kanäle, Konflikte mit Auflösung, Antons Entscheidungen | Claude, wartet auf Anton |
| `06-kundenakten-evidenz-2026-10-31.md` | Sieben Chancen mit Fakten, Reibung, Preisfakten, offene Fragen | Claude |
| `decisions.md` | Entscheidungslog, eine Zeile je Entscheidung mit Grund, Quelle, Status | laufend |
| `agent2/` | Originaldateien des zweiten Agenten, unverändert | zweiter Agent |

Regeln: neue Dokumente nummeriert und datiert; Positionierung ändert sich nur als neue Version von 05; jede Regeländerung eine Zeile in `decisions.md`; nichts hier wird ohne Antons Wort in Code oder Prompt übernommen. PDFs: `python3 ~/.claude/templates/alpitype_doc.py <md> <out> --pdf`.

Verwandt: `docs/handover/` (Übergaben, Pläne, Stand vom 30./31.10.), `openspec/changes/engagement-posts/`, `~/dev/campaign/inbound-log.csv`.
