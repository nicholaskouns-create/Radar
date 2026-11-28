# Grid × Radar multimodal observatory

## Interfaces

- [Radar live instrument](https://nicholaskouns-create.github.io/Radar/doppler/)
- [Grid live instrument](https://nicholaskouns-create.github.io/Identity/grid/radar/)
- [Grid integrated map](https://nicholaskouns-create.github.io/Identity/grid/)
- [Synthetic complex-I/Q atlas](https://nicholaskouns-create.github.io/Radar/optical-radar-atlas/)
- [E47 spectral radar bridge](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-radar-bridge/)

## Source boundary

**Five independent overlays share the map but not their measurement physics.**

| Layer | Publisher | Evidence class | Field |
|---|---|---|---|
| MRMS | NOAA/NWS | LIVE request | observed precipitation radar reflectivity; dBZ colors |
| Quakes | USGS | LIVE request | earthquake coordinates and magnitude, last 24 hours |
| Fires | NIFC WFIGS | LIVE request | published wildfire incident points |
| Severe alerts | NWS API | LIVE request | mapped warning polygons |
| Aurora | NOAA SWPC OVATION | LIVE request / FORECAST | model forecast sampled to map points |
| Generating plants | WRI + EIA historical inventory | PUBLISHED | historical nameplate capacity, coordinates |

The Doppler page title is an inherited application label. MRMS reflectivity **does not provide radial Doppler velocity** in this integration. None of these public geographic feeds supplies raw complex ADC/IQ. The phase, gradient, curvature, coherence, CFAR and E47 analyses are independently represented in the **synthetic educational atlas** and Radar Python research modules.

## Multimodal models

### Facility-event proximity

Geodesic great-circle distance on the sphere (Earth radius 6371 km):

d = 2R asin(sqrt(sin²(Δφ/2) + cos φ₁ cos φ₂ sin²(Δλ/2))).

The instrument computes **plant-event pairs within a user-set radius** for mapped USGS earthquakes and NIFC fires. Each unique plant is counted once for the deduplicated plant total, while pair counts may count multiple nearby events. MW means **historical nameplate capacity**, not current dispatch or at-risk generation.

### NWS warning intersections

For Polygon/MultiPolygon geometry, browser-side point-in-polygon ray crossing, excluding interior holes, counts generating-plant coordinates inside mapped NWS warning polygons. A single plant may intersect more than one warning. The result is geographical exposure screening and carries no outage, damage or causal inference.

### Persistence and exports

Preset name, independent layer switches, proximity radius and map center/zoom are persisted in localStorage on that particular browser/origin. No server-side configuration storage, credentials, or user data write is made. Exported JSON contains source labels, counts, selected settings and retrieval annotations, not the full underlying datasets.

## Provenance and conceptual references

The source registry, normalizers and fetchers come from `Identity/grid/live/sources.js`; the base MRMS overlay comes from `Identity/grid/live/radar.js`. The multimodal implementation is `Identity/grid/live/multimodal.js`; Radar links to the same module without cloning the publisher integration.

The source-focused research survey also consulted the Google Drive documents **KKP-RADAR Technology Concept Proposal Package**, **TECHNICAL MANUAL: PQSPI-ETNS INTEGRATED ONTOLOGICAL RADAR**, and **ARCHIVAL COMPILATION: PQSPI-ETNS INTEGRATED ONTOLOGICAL RADAR**. The concept proposal's feature families are energy/coherence, spatial gradient, curvature, phase and anomaly scoring. They are not claimed as measured outputs of this geographic instrument. The archived papers include claims and illustrative data that require separate empirical evaluation; no operational detection effectiveness is inferred.

For measured ADC: `Radar/src/e47_radar/calibrated_fmcw.py` implements physically calibrated range–Doppler processing and CA-CFAR, and `Radar/src/e47_radar/spectral.py` implements the E47 operator. These paths are **linked**, not executed against the NOAA pixel imagery.

## Tests and limitations

- Deterministic JS geometry, polygon containment, source parser and tile URL tests: `Identity/tools/grid/test_multimodal_radar.mjs`.
- CI source checks: `Identity/.github/workflows/grid-multimodal-radar.yml`.
- Each public feed is fetched only when its option is enabled; disabled and unreachable feeds report their status without synthetic substitution.
- Browser-level live rendering, publisher freshness and GitHub Pages deployment must be checked separately from source commits.
- The repository survey examined twelve accessible GitHub repositories and their tree/file references. This was **not** an end-to-end execution of all twelve repositories.
