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
