# Piper HTTP TTS für Home Assistant

Home Assistant TTS-Plattform für lokale Sprachausgabe via [Piper HTTP Server](https://github.com/Zeronova/piper-http). Unterstützt dynamisches Model-Switching, Denglisch-Ersetzungen und mehrere Audio-Formate.

## Installation

### Via HACS (empfohlen)

1. HACS → Custom Repositories → `https://github.com/zeronova/HA_piper-http` (Typ: Integration)
2. HACS → Integrationen → "Piper HTTP" installieren
3. HA neu starten

### Manuell

1. Ordner `piper_http` nach `custom_components/piper_http` kopieren
2. HA neu starten

## Konfiguration

1. **Integration hinzufügen:** Einstellungen → Geräte & Dienste → Integration hinzufügen → "Piper HTTP"
2. **Host und Port** des Piper-Servers angeben
3. **Assistent einrichten:** Einstellungen → Sprachassistenten → Assist → Text-zu-Sprache → "Piper HTTP" auswählen

| Option | Standard | Bereich |
|--------|----------|---------|
| Model | erstes Fallback | via FALLBACK_MODELS |
| Speaker ID | 1 | 0–8 |
| Length Scale | 1.0 | 0.1–5.0 |
| Noise Scale | 0.667 | 0.0–2.0 |
| Noise W | 0.8 | 0.0–2.0 |
| Sentence Silence | 0.5 | 0.0–10.0 |
| Denglisch | ein | ein/aus |
