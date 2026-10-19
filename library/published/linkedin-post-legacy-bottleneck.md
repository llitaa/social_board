# LinkedIn-Post: Was KI-Tools in Legacy-Systemen nie lösen (Anton, Expert-Post)

**Konto:** Anton persönlich · **Sprache:** DE · **Typ:** Expertise/Authority
**Ziel:** Projektanfragen C++/Qt — der Post soll den Leser denken lassen „genau das haben wir gerade"
**Slot-Vorschlag:** Di oder Mi 07:30–08:30 · kein Link im Text

---

## Text

Der Punkt, an dem KI-Werkzeuge in Legacy-Code aufhören zu helfen, ist nicht die Sprache. Es ist der Moment, in dem der Engpass nicht eindeutig ist.

Ein Muster, das ich in fast jedem gewachsenen System sehe: Sie bauen einen Cache in die Datenschicht. Der Batch-Betrieb wird dreimal schneller. Zwei Wochen später meldet der Servicetechniker, dass seine Live-Diagnose veraltete Werte zeigt — er war der Einzige, der auf ungecachte Frische angewiesen war.

Beide Abläufe sind korrekt implementiert. Der Konflikt zwischen ihnen steht nirgends im Code.

Genau da ist die Grenze. KI-Werkzeuge sind stark bei lokalen Transformationen: Funktion extrahieren, API portieren, Test für reine Logik schreiben. Den Kompromiss zwischen zwei Abläufen sehen sie nicht — weil er nicht im Repository liegt. Er liegt in Messungen, im Laufzeitverhalten und in einer Frage, die kein Modell beantworten kann: Welcher Ablauf darf schlechter werden?

Das ist eine Priorisierungsentscheidung, keine Programmieraufgabe. Sie braucht jemanden, der beide Abläufe misst, bevor er eine Zeile ändert — und der hinterher zeigen kann, dass der zweite nicht schlechter geworden ist.

Deshalb beginne ich solche Projekte nicht mit Refactoring, sondern mit zwei Messungen und einem Gespräch mit dem, der die Maschine tatsächlich bedient.

Ich arbeite freiberuflich an genau solchen Systemen: C++/Qt, Steuerungs- und Bediensoftware. Wenn Ihres gerade an dieser Stelle steht — schreiben Sie mir kurz.

#Cplusplus #Qt #Industriesoftware

---

## Alternative Hooks (für A/B beim nächsten Mal)

- „Ein KI-Tool kann Ihren Code umbauen. Es kann Ihnen nicht sagen, welcher Ablauf schlechter werden darf."
- „Der teuerste Satz in einem Legacy-Projekt: ‚Bei uns ist es jetzt schneller.' — Bei wem, in welchem Ablauf?"
- „Nach dem Refactoring war der Batch dreimal schneller. Und der Servicetechniker konnte nicht mehr arbeiten."

## Umsetzung

- **Bild:** `IMG_5820.HEIC` (Selfie vor der Hochschule München, 22.08.2026) — hochkant gedrehte Fassung: `IMG_5820_upright.jpg`. Gesicht + Deutsch ist laut `posts-log.csv` die bisher stärkste Kombination (li-post-02).
  Alt-Text: „Selfie von Anton Lytvynenko im Freien vor dem Gebäude der Hochschule München, sonniger Spätsommertag."
  Hinweis: Das Foto hat keinen inhaltlichen Bezug zum Thema. Falls der Besuch einen Anlass hatte (Vortrag, Gespräch, Lehrauftrag), gehört ein Halbsatz dazu in die erste oder letzte Zeile — sonst wirkt es als reines Gesichts-Bild, was für Reichweite reicht, aber Substanz verschenkt.
- **Kein Link.** Die letzte Zeile ist der CTA — DMs sind hier das Ziel, nicht Klicks.
- **Kommentare vorbereiten:** Wer „welche Messungen?" fragt, bekommt eine konkrete Antwort (z. B. Latenz pro Nutzer-Flow statt Gesamtdurchsatz, vorher/nachher am selben Datensatz). Solche Antworten erzeugen den zweiten Sichtbarkeitsschub.
- **Zielgruppen-Filter beim Posten:** DE / Maschinenbau, Medizintechnik, Halbleiter, Automation / Engineering + IT-Leitung.
- **Nachfassen:** Wer den Post kommentiert oder speichert, ist ein warmer Kontakt für die Buch-/Freelance-Chain in `prospects.csv`.
