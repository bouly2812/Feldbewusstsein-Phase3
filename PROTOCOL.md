# Prüfprotokoll Strang 3 – Feldbewusstsein

## Parameterrahmen
- **Basis-/Nullfenster (T_base):** Definierter Zeitraum vor Anregung zur Bestimmung des
  Grundrauschens und der natürlichen Schwankung von `rho`, `Psi` und `c(rho, Psi)`.
- **Anregungs- / Kopplungsfenster (T_coup):** Schrittweise oder getaktete Variation
  von Kopplungs- und Feldbedingungen.
- **Nachlauf- / Persistenzfenster (T_post):** Beobachtungszeitraum nach Abschalten oder
  Absenken des äußeren Reizes, um anhaltende Zustandsänderungen von bloßen
  Reizantworten zu trennen.

## Zeitachsen-Übersicht des Testlaufs

```text
Zeit:   0.0s -------- 1.5s | 2.0s  2.5s | 3.0s ---------------- 5.5s | 6.0s -------- 7.5s
Phase:  [--- Baseline ---] | [Stör-Flags] | [--- Kopplungsfenster ---] | [--- Nachlauf ---]
Status:  niedriges c       | ext/Metall   | c steigt -> Z=1 bei 5.5s   | Abklingen / Halten