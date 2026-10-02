# ddj-flx4-djmixer

DDJ-FLX4 DJ Mixer browser implementation with a built-in MIDI controller map.

## Source layout

- `mixer.fragment.html` — self-contained mixer UI and Web MIDI integration
- `index.html` — deployable static bundle
- `export-site.py` — regenerates `index.html` from the mixer fragment
- `.openai/hosting.json` — Sites static-host configuration

The hosted DDJ-FLX4 Mixer remains deployed through its managed Sites source
repository. This GitHub repository mirrors the source and deployable bundle for
version control and review.
