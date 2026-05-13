# Piper HTTP TTS

Ein benutzerdefinierter **TTS-Provider** für Home Assistant, der direkten HTTP-Zugriff auf einen [piper-http](https://github.com/Zeronova/piper-http) Server ermöglicht – ohne Wyoming-Addon, mit GPU-Beschleunigung.

## Motivation

Der offizielle Wyoming-Piper startet pro Anfrage einen neuen Prozess – das ist langsam und nutzt keine GPU.  
**piper-http** läuft als persistenter Server mit CUDA/CUDAExecutionProvider und bleibt zwischen Anfragen warm.

## Features

- ⚡ **Schnell** – kein Prozess-Start pro Anfrage (GPU-beschleunigt via CUDA)
- 🎛️ **Voll konfigurierbar** – Modell, Sprecher-ID, Geschwindigkeit, Rauschparameter via UI
- 🔄 **Model-Switching** – Server-Modell wird bei Änderung automatisch umgeschaltet
- 🌐 **Native HA Integration** – Config Flow via UI, kein YAML nötig
- 🔊 **OGG/WAV** – unterstützt beide Formate (abhängig vom Server)
- 🇩🇪 **Mehrere Stimmen** – Jarvis, Thorsten, Pavoque, Glados uvm.

## Installation

### Via HACS (Custom Repository)

1. HACS → Integrationen → Drei Punkte → Custom Repositories
2. URL: `https://github.com/Zeronova/HA_piper-http`
3. Kategorie: **Integration**
4. HACS durchsuchen → "Piper HTTP TTS" → Installieren
5. Home Assistant **neu starten**

### Manuell

1. Kopiere `custom_components/piper_http/` in dein HA `custom_components/` Verzeichnis
2. Home Assistant **neu starten**

## Konfiguration

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach **Piper HTTP TTS** suchen
3. **Host** und **Port** deines piper-http Servers eingeben (Standard: `192.168.2.7:5000`)
4. Verbindung wird getestet – verfügbare Modelle geladen
5. Fertig

### Optionen anpassen

Nach der Installation kannst du unter *Integration → Piper HTTP TTS → Konfigurieren* folgende Parameter ändern:

| Option | Beschreibung | Standard |
|--------|-------------|---------|
| **Modell** | Aktive Stimme | Erstes gefundenes Modell |
| **Sprecher-ID** | Multi-Speaker Modell (0–10) | 1 |
| **Sprechgeschwindigkeit** | Geschwindigkeit (0.3–3.0) | 1.0 |
| **Rauschskala** | Tonhöhenvariation (0.0–2.0) | 0.667 |
| **Rauschbreite** | Variationsbreite (0.0–2.0) | 0.8 |
| **Satz-Pause** | Pause zwischen Sätzen (0–10s) | 0.0 |

## Verwendung

Nach der Konfiguration steht **Piper HTTP TTS** als TTS-Engine in:

- **Automationen** → `tts.speak` → Wähle `tts.piper_http`
- **Voice Pipelines** → Als TTS-Engine auswählen
- **YAML** → `service: tts.speak` mit `entity_id: tts.piper_http`

### Beispiel Automation

```yaml
action:
  service: tts.speak
  target:
    entity_id: tts.piper_http
  data:
    media_player_entity_id: media_player.wohnzimmer
    message: "Guten Morgen.; Es ist 7 Uhr und die Sonne scheint."
```

## Voraussetzungen

- Home Assistant **2026.4** oder neuer
- **piper-http Server** läuft erreichbar im Netzwerk
- Python 3.14+

## API

Der TTS-Provider ruft deinen piper-http Server auf:

```
GET http://{host}:{port}/?text=Hallo+Welt&speaker_id=1&length_scale=1.0
```

Modell-Wechsel via:

```
POST http://{host}:{port}/voice
{"model": "de_DE-thorsten-high.onnx"}
```

## Lizenz

MIT
