# Ein Paper oder eine Korrektur beitragen

Ein Beitrag kann einen neuen Befund, eine Reproduktion, einen Gegenbefund oder eine Korrektur dokumentieren. Die folgende Vorlage steht beim Anlegen eines Issues als „Neuer Beleg“ bereit und eignet sich auch als Beschreibung eines Pull Requests. Für einen Einwand gegen einen bestehenden Eintrag gibt es die Vorlage „Einwand oder Korrektur“. Wer die Daten direkt ändert, legt die YAML-Dateien nach [Datenmodell und Aufbau auf GitHub](docs/03-datenmodell-und-github.md) an und prüft sie mit `python scripts/atlas.py validate`.

## Kopiervorlage

```markdown
### Forschungsfrage und Aussage

- Forschungsziel und Meilenstein-ID:
- Zu prüfende Aussage in einem Satz:
- Geltungsbereich (z. B. Datensatz, Instrument, Population oder Voraussetzungen):

### Fundstelle und Ergebnis

- Studie, DOI oder persistenter Link, verwendete Fassung:
- Fundstelle (Seite, Abschnitt, Abbildung oder Tabellenzeilen):
- Messgröße, Einheit und Vergleich:
- Ergebnis und angegebene Unsicherheit:
- Datensatz- oder Ereignis-ID und bekannte Überschneidungen:

### Einordnung

- Verhältnis zur Aussage (stützt / spricht dagegen / nicht entscheidend):
- Begründung und wichtigste Einschränkung:
- Bei einer Korrektur: bisherige Einstufung und betroffener Eintrag:
- Nächste fachliche Prüfung:
```

## Prüfung vor der Freigabe

- [ ] Die angegebene Fassung enthält die Fundstelle.
- [ ] Zahlen, Einheiten und Vergleich stimmen mit der Quelle überein.
- [ ] Der Wortlaut der Aussage bleibt innerhalb der untersuchten Bedingungen.
- [ ] Wiederverwendete Daten und verbundene Publikationen sind zugeordnet.
- [ ] Bekannte Gegenbefunde und Unsicherheiten stehen im Eintrag.
- [ ] Eine zweite Person hat die Einordnung geprüft und die Entscheidung begründet.

Bleibt eine Frage strittig, dokumentieren beide Personen, worüber sie sich einig sind und welche zusätzliche Information den Dissens klären könnte.

