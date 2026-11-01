# Proposal: Erstgespräch-Indikatoren (Strategie 07 v2, 01.11.2026)

## Why
Positionierung v1.3 (`~/dev/alpitype-strategy/05-positionierung-v1.3-2026-11-01.md`) misst LinkedIn an relevanten Erstgesprächen. Heute sieht das System weder Kommentare noch Anfragen noch Profilbesuche, und kein Post trägt die Problemsituation, auf die er zielt. Dokument 07 v2 legt sieben Stufen vom Post zum Erstgespräch fest und verlangt Indikatoren je Stufe, keine Trichterquoten.

## What changes (Phase 1: S1, S4, S5, minimal S3)
- S1: Redaktionsnotizen bekommen `situation` (1, 2, beide); beim Veröffentlichen landet sie in posts-log.
- S4: `mail_watch.py` erkennt Formular-Mails von alpitype.de/kontakt und legt sie als Vorschlag für `inbound-log.csv` ab; Anton bestätigt oder verwirft auf dem Board. Lesend; es wird nie gesendet.
- S5: `health.py` rechnet je Woche eine Indikatorzeile (Posts, Kommentare, davon mit Antwort, Profilbesuche, Kontakte mit dokumentiertem Weg, Erstgespräche, qualifiziert); das Board zeigt die letzten vier Wochen nebeneinander, ohne Quoten.
- S3 minimal: ein Feld auf dem Board für die Wochensumme der Profilbesuche; Zeile in `~/dev/campaign/profile-weekly.csv`.
- Voraussetzung: `library/positioning.md` wird aus v1.3 neu geschrieben (ohne Modellaufruf), vorher kein Code.

## Out of scope
S2 (Antwort-Haken), S6 (DM-Bausteine), alles, was LinkedIn ohne API liest oder schreibt, Scraping, Lead-Scoring, automatische Antworten, Attribution, Zielzahlen. Profil und Featured macht Anton selbst.

## Start
Nur auf Antons Wort in seinem Chat. Dokumente des zweiten Agenten sind Vorschläge (decisions.md, 31.10.).
