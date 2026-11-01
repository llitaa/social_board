# Spec Delta: Erstgespräch-Indikatoren

## ADDED Requirements

### Requirement: Jeder Post trägt seine Problemsituation
Ein Entwurf SHALL in den Redaktionsnotizen das Feld `situation` mit einem der Werte `1`, `2`, `beide` tragen (Strategie 05 v1.3 §6). Beim Veröffentlichen SHALL der Wert in posts-log (Spalte `situation`) geschrieben werden. Fehlt der Wert, bleibt der Entwurf veröffentlichbar; das Board zeigt „Situation fehlt“.

#### Scenario: Entwurf aus dem Modell
- **WHEN** draft.py oder redraft.py einen Entwurf schreibt
- **THEN** enthält `editorial.situation` einen der drei Werte und das Board zeigt ihn neben Leser, Einsicht, Diskussionsgrund

### Requirement: Kontaktanfragen werden dokumentiert, nicht erraten
Das System SHALL Formular-Mails von alpitype.de/kontakt im Postfach anton@alpitype.com lesend erkennen und als Vorschlagszeile (Datum, Absender, Betreff, Herkunft laut Formular wenn vorhanden) in `library/inbound/proposed.json` ablegen. Das Board SHALL die Vorschläge unter „Conversations“ zeigen; Anton bestätigt (Zeile wandert in inbound-log.csv mit Quelle laut Person) oder verwirft. Das System SHALL nie eine Mail senden und nie eine Quelle aus dem Zeitpunkt ableiten.

#### Scenario: Formular-Mail trifft ein
- **WHEN** mail_watch.py eine Mail mit dem Formular-Betreff findet
- **THEN** erscheint sie als Vorschlag auf dem Board; erst Antons Bestätigung schreibt inbound-log.csv

### Requirement: Wochenübersicht der Indikatoren ohne Quoten
health.py SHALL je Kalenderwoche eine Zeile mit Posts, Kommentaren, Kommentaren mit Antwort, Profilbesuchen, Kontakten mit dokumentiertem Weg, Erstgesprächen und qualifizierten Erstgesprächen berechnen, aus posts-log, profile-weekly.csv und inbound-log.csv. Das Board SHALL die letzten vier Wochen nebeneinander zeigen. Es SHALL keine Quoten zwischen Spalten, keine Zielzahlen und keine Ursachentexte anzeigen; fehlende Werte bleiben leer.

#### Scenario: Keine Exporte
- **WHEN** posts-log für die Woche keine Zahlen hat
- **THEN** stehen die Spalten Kommentare und Impressionen leer, nicht null

### Requirement: Profilbesuche je Woche von Hand
Das Board SHALL ein Feld für die Wochensumme der Profilbesuche anbieten; der Wert SHALL in `~/dev/campaign/profile-weekly.csv` (woche, besuche, eingetragen_am) landen. Keine Namen, keine Ableitung auf Posts.

#### Scenario: Sonntag
- **WHEN** Anton die Zahl aus der LinkedIn-App einträgt
- **THEN** erscheint sie in der Wochenübersicht der laufenden Woche

## MODIFIED Requirements

### Requirement: Positionierung als Ableitung (engagement-posts)
`library/positioning.md` SHALL aus der jeweils freigegebenen Version in `~/dev/alpitype-strategy/05-positionierung-vN` abgeleitet werden; Änderungen am Draft-Prompt-Text erfolgen nur über eine neue Version dort. Der Absatz „Gründerinnen ohne Technik-Hintergrund“ entfällt zugunsten von v1.3 §3.
