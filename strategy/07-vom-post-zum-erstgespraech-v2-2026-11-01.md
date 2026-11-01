title: 07 Vom Post zum Erstgespräch, Version 2
subtitle: Version 2 mit den vier Korrekturen des zweiten Agenten: Indikatoren statt Trichter, keine vorschnelle Ursache, Featured nach Relevanz, Antworten und Zeit als Budget. Wartet auf Anton
footer: AlpiType · Intern · Strategie 07 · Version 2 · 01.11.2026

<style>table{page-break-inside:auto} tr{page-break-inside:avoid}</style>

## 1. Ausgangslage, ehrlich

Es gibt noch keinen einzigen Fall, in dem ein Post zu einem Erstgespräch geführt hat. Die Stufen unten sind deshalb ein Vorschlag, wie der Weg aussehen müsste, und eine Zählung, die zeigt, wo er abreisst. Vieles davon kann das System nicht sehen: LinkedIn gibt keine API für Kommentare, Direktnachrichten oder Profilbesuche frei; Scraping und Automatisierung von Anfragen sind ausgeschlossen (Nutzungsbedingungen und Antons Regel). Was das System sehen kann: Exporte mit Zahlen je Post, den Posteingang anton@alpitype.com lesend (Graph, nur lesen), die Kontaktseite alpitype.de/kontakt, und alles, was Anton in eine Zeile schreibt.

## 2. Die Stufen und wer sie sieht

| Stufe | Was passiert | Wer sieht es | Was zählt |
|---|---|---|---|
| 1 Post | Eine erzählte Situation (1 oder 2), Redaktionsnotizen mit Situation, Leser, Einsicht, Diskussionsgrund | System (Board) | Situation je Post |
| 2 Reaktion | Kommentar, Reaktion, Repost | Export alle zwei Wochen (Zahlen); Kommentartext nur Anton in der App | Kommentare gesamt; davon relevante (Antons Urteil: eine Person mit dem Problem oder in der Rolle) |
| 3 Antwort | Anton antwortet, wo eine Antwort etwas beiträgt; keine Pflichtreaktion, kein Ein-Satz-Reflex, kein Angebot | Anton | Kommentare mit Antwort (Board-Haken je Post, Antons Urteil) |
| 4 Profil | Der Leser öffnet das Profil: Headline, Info-Abschnitt, Featured, Kontaktweg | LinkedIn zeigt die Wochensumme der Profilbesuche; Namen nur Premium | Profilbesuche je Woche (eine Zahl, von Anton eingetragen) |
| 5 Kontakt | DM auf LinkedIn, Vernetzungsanfrage mit Notiz, Kontaktformular, Mail | DM: Anton. Formular und Mail: System lesend (mail_watch), Anton | Zeile im inbound-log, Quelle „LinkedIn“, Situation, Post-ID wenn genannt |
| 6 Erstgespräch | 30 Minuten mit einem Ingenieur (Teams oder Telefon) | Anton | Zeile im inbound-log: qualified ja oder nein |
| 7 Danach | Analysephase, Betriebs-Check, Angebot; oder nichts | Kundenakte | Vertrieb, nicht LinkedIn |

Die Stufen sind kein Trichter: wir wissen nicht, ob dieselben Personen sie durchlaufen. Profilbesuche sind eine Wochensumme ohne Namen, Kommentare stammen von anderen Leuten als die Anfragen. Gezählt werden deshalb **Indikatoren je Stufe** und **dokumentierte Kontaktwege** (was die Person selbst über ihren Weg sagt), keine Conversion-Raten zwischen Stufen.

## 3. Was am Profil sein muss (Stufe 4), einmalig, von Anton

| Element | Heute (Firmenkontext 26.08.) | Vorschlag |
|---|---|---|
| Headline | „Freelance C++/Qt Software Engineer und Software Architect“ (zu prüfen) | „Software Architect & Technical Lead · Industrielle Software, die in der Produktion läuft · Engineering Leadership“. Ohne Freelance, ohne KI-Schlagwort. |
| Info-Abschnitt | nicht geprüft | Drei Absätze: was er getragen hat (Branchen, Teams, Produktion), was er heute tut (Architektur, Agents in echtem Code, 70/30), ein Satz Kontaktweg: „Wenn Sie eine Situation aus meinen Beiträgen wiedererkennen: 30 Minuten mit mir, alpitype.de/kontakt oder Nachricht hier.“ |
| Featured | nicht gepflegt | Drei Posts, die zusammen drei Dinge zeigen: technische Glaubwürdigkeit (ein Fallpost aus der Produktion), ein konkretes Kundenproblem (eine Situation 1 oder 2) und Antons persönliche Verantwortung (eine Entscheidung, die er getragen hat). Anton wählt sie; Impressionen sind nur ein Hinweis. Die Impressions-Liste des Boards (pipeline.json „featured“) bleibt als Hinweis, nicht als Auswahl. |
| Kontaktseite | alpitype.de/kontakt: „Sprechen Sie mit einem Ingenieur“, Antwort binnen 24 h | Bleibt. Ergänzung: ein Feld „Woher kennen Sie uns?“ (LinkedIn, Empfehlung, Suche, Messe), damit die Quelle vom Kontakt kommt, nicht aus Antons Vermutung. Website-Änderung, Antons Entscheidung. |

## 4. Was Anton tut, mit Zeitbudget als Obergrenze, nicht als Pflicht

| Wann | Was | Zeit |
|---|---|---|
| An Posttagen, am Abend | Kommentare lesen; antworten, wo es etwas beiträgt, in der Länge, die die Sache braucht; Vernetzungsanfragen von Kommentierenden annehmen; eine Vernetzung mit Notiz an eine Person, deren Kommentar eine Situation zeigt, wenn es sich ergibt | bis 15 Minuten |
| Bei jeder DM oder Formularanfrage | Innerhalb eines Werktags antworten: eine Rückfrage zur Situation, dann Terminvorschlag für 30 Minuten; kein Dokument, kein Angebot vor dem Gespräch | 5 Minuten je Fall |
| Wöchentlich, Sonntag | Profilbesuche der Woche von LinkedIn ablesen und auf dem Board eintragen; inbound-log ergänzen; Haken „Kommentare beantwortet“ je Post der Woche | 10 Minuten |
| Alle zwei Wochen | Zwei Exporte in Downloads | 5 Minuten |

Was Anton nicht tut: Serien-Vernetzungsanfragen, Kommentare unter fremden Posts als Taktik, Nachfassen bei Menschen, die nicht geantwortet haben, Angebote in der DM vor dem Gespräch.

## 5. Was das System übernimmt (Vorschlag, nicht umgesetzt)

| # | Baustein | Was es tut | Aufwand | Modellaufruf |
|---|---|---|---|---|
| S1 | Situation je Post | Redaktionsnotizen bekommen das Feld „situation“ (1, 2, beide); cards.py schreibt es nach posts-log beim Veröffentlichen | 1 Stunde | nein |
| S2 | Antwort-Haken | Unter „Published“ je Post der letzten 7 Tage ein Haken „Kommentare beantwortet“ und ein Feld „relevante Kommentare“ (Zahl); landet in posts-log | 2 Stunden | nein |
| S3 | Profilbesuche je Woche | Ein Feld auf dem Board, eine Zeile in `~/dev/campaign/profile-weekly.csv`; gezeigt als kleine Reihe | 1 Stunde | nein |
| S4 | Kontaktformular lesen | mail_watch.py liest heute nur LinkedIn-Mails; Erweiterung: Formular-Mails von alpitype.de erkennen und als Zeile „neu, Quelle laut Formular“ ins inbound-log vorschlagen, Anton bestätigt auf dem Board | 3 Stunden | nein |
| S5 | Wochenübersicht der Indikatoren | health.py rechnet aus posts-log, profile-weekly und inbound-log eine Zeile je Woche: Posts, Kommentare, davon mit Antwort, Profilbesuche, Kontakte mit dokumentiertem Weg, Gespräche; Board zeigt die letzten vier Wochen nebeneinander, ohne Quoten zwischen den Spalten | 2 Stunden | nein |
| S6 | DM-Bausteine | Drei Texte in `library/dm/`: Rückfrage zur Situation 1, zur Situation 2, Terminvorschlag. Anton kopiert von Hand; das System sendet nie | 30 Minuten | nein |
| S7 | Featured-Hinweis | existiert (cards.py, nach Impressionen); bleibt Hinweis; die Auswahl nach Abschnitt 3 trifft Anton | 0 | nein |

Reihenfolge laut zweitem Agenten: zuerst S1, S4, S5 (Situation je Post, Kontaktanfragen dokumentieren, einfache Übersicht); danach S2, S3, S6 nur, wenn sie zusätzliche Erkenntnis bringen. Voraussetzung vor jedem Code: positioning.md aus v1.3 neu geschrieben, auf Antons Wort.

Nicht gebaut: alles, was LinkedIn liest oder schreibt ohne API (Kommentare, DMs, Profilbesucher, Vernetzung), Scraping, Lead-Scoring, automatische Antworten, Attribution von Projekten auf Posts, Conversion-Raten zwischen Stufen.

## 6. Was gezählt wird, und was eine Zahl nicht bedeutet

Wöchentliche Indikatorzeile (S5): Posts · Kommentare · davon mit Antwort · Profilbesuche (Wochensumme) · Kontakte mit dokumentiertem Weg (DM, Formular, Mail; Quelle laut Person) · Erstgespräche · davon qualifiziert. Je Kontakt die Situation, wenn die Person oder der genannte Post sie erkennen lässt.

Keine Zielzahlen in den ersten sechs Wochen. Keine automatische Ursache: ausbleibende Kommentare und Profilbesuche können an Inhalt, Reichweite oder Zielgruppenpassung liegen; Profilbesuche ohne Anfragen beweisen nichts über die Kontaktseite. Nach sechs Wochen liest Anton die Zeilen zusammen mit den Exporten und entscheidet, an welcher Stufe gearbeitet wird; das Dokument legt die Lesart nicht vorab fest.

## 7. Was Anton entscheidet

1. Profil nach Abschnitt 3 ändern (Headline, Info, Featured nach Relevanz): Anton selbst, Termin.
2. Kontaktseite um ein optionales Feld „Woher kennen Sie uns?“ ergänzen: ja oder nein.
3. Zeitbudget nach Abschnitt 4 als Obergrenze: ja oder anders.
4. System-Bausteine gestaffelt: erst S1, S4, S5 (etwa sechs Stunden), später S2, S3, S6 bei Bedarf. Vorher positioning.md aus v1.3. Alles ohne Modellaufruf. Start nur auf Antons Wort.
5. Sechs Wochen beobachten ohne Zielzahl und ohne vorab festgelegte Schuldzuweisung: ja oder nein.
