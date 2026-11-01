title: 07 Vom Post zum Erstgespräch
subtitle: Wie aus LinkedIn-Beiträgen relevante Erstgespräche entstehen: die Stufen, was davon sichtbar ist, was das System übernimmt, was Anton tut, was gezählt wird. Entwurf, wartet auf Anton
footer: AlpiType · Intern · Strategie 07 · Entwurf 01.11.2026

<style>table{page-break-inside:auto} tr{page-break-inside:avoid}</style>

## 1. Ausgangslage, ehrlich

Es gibt noch keinen einzigen Fall, in dem ein Post zu einem Erstgespräch geführt hat. Die Stufen unten sind deshalb ein Vorschlag, wie der Weg aussehen müsste, und eine Zählung, die zeigt, wo er abreisst. Vieles davon kann das System nicht sehen: LinkedIn gibt keine API für Kommentare, Direktnachrichten oder Profilbesuche frei; Scraping und Automatisierung von Anfragen sind ausgeschlossen (Nutzungsbedingungen und Antons Regel). Was das System sehen kann: Exporte mit Zahlen je Post, den Posteingang anton@alpitype.com lesend (Graph, nur lesen), die Kontaktseite alpitype.de/kontakt, und alles, was Anton in eine Zeile schreibt.

## 2. Die Stufen und wer sie sieht

| Stufe | Was passiert | Wer sieht es | Was zählt |
|---|---|---|---|
| 1 Post | Eine erzählte Situation (1 oder 2), Redaktionsnotizen mit Situation, Leser, Einsicht, Diskussionsgrund | System (Board) | Situation je Post |
| 2 Reaktion | Kommentar, Reaktion, Repost | Export alle zwei Wochen (Zahlen); Kommentartext nur Anton in der App | Kommentare gesamt; davon relevante (Antons Urteil: eine Person mit dem Problem oder in der Rolle) |
| 3 Antwort | Anton antwortet auf jeden relevanten Kommentar innerhalb von 24 Stunden mit einem Satz, ohne Angebot | Anton | Antwortquote (Board-Haken) |
| 4 Profil | Der Leser öffnet das Profil: Headline, Info-Abschnitt, Featured, Kontaktweg | LinkedIn zeigt die Wochensumme der Profilbesuche; Namen nur Premium | Profilbesuche je Woche (eine Zahl, von Anton eingetragen) |
| 5 Kontakt | DM auf LinkedIn, Vernetzungsanfrage mit Notiz, Kontaktformular, Mail | DM: Anton. Formular und Mail: System lesend (mail_watch), Anton | Zeile im inbound-log, Quelle „LinkedIn“, Situation, Post-ID wenn genannt |
| 6 Erstgespräch | 30 Minuten mit einem Ingenieur (Teams oder Telefon) | Anton | Zeile im inbound-log: qualified ja oder nein |
| 7 Danach | Analysephase, Betriebs-Check, Angebot; oder nichts | Kundenakte | Vertrieb, nicht LinkedIn |

Abbruchstellen, an denen die Zählung Auskunft geben wird: zwischen 2 und 3 (Anton antwortet nicht), zwischen 3 und 4 (das Profil sagt nichts), zwischen 4 und 5 (kein Kontaktweg), zwischen 5 und 6 (Anton antwortet auf DMs zu spät oder mit Angebot statt Termin).

## 3. Was am Profil sein muss (Stufe 4), einmalig, von Anton

| Element | Heute (Firmenkontext 26.08.) | Vorschlag |
|---|---|---|
| Headline | „Freelance C++/Qt Software Engineer und Software Architect“ (zu prüfen) | „Software Architect & Technical Lead · Industrielle Software, die in der Produktion läuft · Engineering Leadership“. Ohne Freelance, ohne KI-Schlagwort. |
| Info-Abschnitt | nicht geprüft | Drei Absätze: was er getragen hat (Branchen, Teams, Produktion), was er heute tut (Architektur, Agents in echtem Code, 70/30), ein Satz Kontaktweg: „Wenn Sie eine Situation aus meinen Beiträgen wiedererkennen: 30 Minuten mit mir, alpitype.de/kontakt oder Nachricht hier.“ |
| Featured | nicht gepflegt | Die drei Posts mit den meisten Impressionen der letzten 90 Tage; das Board rechnet sie aus (pipeline.json „featured“) und zeigt sie; Anton pinnt sie von Hand. |
| Kontaktseite | alpitype.de/kontakt: „Sprechen Sie mit einem Ingenieur“, Antwort binnen 24 h | Bleibt. Ergänzung: ein Feld „Woher kennen Sie uns?“ (LinkedIn, Empfehlung, Suche, Messe), damit die Quelle vom Kontakt kommt, nicht aus Antons Vermutung. Website-Änderung, Antons Entscheidung. |

## 4. Was Anton tut, mit Zeitbudget

| Wann | Was | Zeit |
|---|---|---|
| An Posttagen, am Abend | Relevante Kommentare beantworten, ein Satz, keine Angebote; Vernetzungsanfragen von Kommentierenden annehmen; selbst eine Vernetzung mit Notiz an eine Person, deren Kommentar eine Situation zeigt | 15 Minuten |
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
| S5 | Trichter je Woche | health.py rechnet aus posts-log, profile-weekly und inbound-log eine Zeile: Posts, Kommentare, relevante, beantwortet, Profilbesuche, Kontakte, Gespräche; Board zeigt die letzten vier Wochen | 2 Stunden | nein |
| S6 | DM-Bausteine | Drei Texte in `library/dm/`: Rückfrage zur Situation 1, zur Situation 2, Terminvorschlag. Anton kopiert von Hand; das System sendet nie | 30 Minuten | nein |
| S7 | Featured-Vorschlag | existiert (cards.py), wird nur sichtbarer gemacht | 30 Minuten | nein |

Nicht gebaut: alles, was LinkedIn liest oder schreibt ohne API (Kommentare, DMs, Profilbesucher, Vernetzung), Scraping, Lead-Scoring, automatische Antworten, Attribution von Projekten auf Posts.

## 6. Was gezählt wird, und was eine Zahl bedeutet

Wöchentliche Zeile (S5): Posts · Kommentare · relevante Kommentare · beantwortet · Profilbesuche · Kontakte (DM, Formular, Mail) mit Quelle LinkedIn · Erstgespräche · davon qualifiziert. Je Kontakt die Situation.

Keine Zielzahlen in den ersten sechs Wochen. Die Zählung soll zeigen, welche Stufe leer bleibt. Zwei Lesarten sind vorab festgelegt: bleiben Kommentare und Profilbesuche aus, liegt es am Inhalt; gibt es Kommentare und Profilbesuche, aber keine Kontakte, liegt es am Profil und am Kontaktweg. Erst dann wird an der jeweiligen Stufe gearbeitet, nicht an allen.

## 7. Was Anton entscheidet

1. Profil nach Abschnitt 3 ändern (Headline, Info, Featured): Anton selbst, Termin.
2. Kontaktseite um „Woher kennen Sie uns?“ ergänzen: ja oder nein.
3. Zeitbudget nach Abschnitt 4: ja oder anders.
4. System-Bausteine S1 bis S7: welche, und wann. Alle ohne Modellaufruf; zusammen etwa zehn Stunden.
5. Sechs Wochen zählen ohne Zielzahl, dann die Abbruchstelle bearbeiten: ja oder nein.
