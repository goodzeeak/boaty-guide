# Boaty Guide RuneLite Plugin

Boaty Guide is a standalone RuneLite plugin for following Boaty's HCIM Guide V3 in a clean bank-by-bank flow.

It focuses on:
- current step
- attached advice for the current step or bank block
- withdraw list for the active bank block
- next steps in the active bank block
- manual progress tracking per RuneLite profile/account

## Credits

This plugin exists because of the work already put into the guide itself.

- Guide content is based on B0aty's HCIM Guide V3 on the OSRS Wiki.
- The source guide credits Tpapa with creating the route structure used as the base for the guide.
- Additional credit also goes to the OSRS Wiki editors and maintainers who helped preserve and publish the guide content that made this plugin possible.


## Build

```powershell
.\gradlew.bat test
```

## Regenerate Guide Data

```powershell
python scripts\parse_guide.py
```

The generator reads:

- `data/raw/guide_v3_raw.txt`
- `data/aliases/*.json`
- `data/overrides/steps.json`

And writes:

- `src/main/resources/com/boatyguide/guide_data.json`
- `data/generated/guide_diagnostics.json`

## Plugin Hub Notes

- Root metadata is in `runelite-plugin.properties`
- Root `icon.png` is sized for Plugin Hub submission
- The runtime guide source is committed JSON, not a live wiki fetch
- Diagnostics are kept out of runtime resources
