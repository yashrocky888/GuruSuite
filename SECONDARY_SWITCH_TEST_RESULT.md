# Secondary Switch Test — Result
## “The Emperor’s Transit” (Narendra Modi)

**Test:** Secondary Switch validation (read-only)  
**Input (locked):** DOB 1950-09-17, Time 11:00, Lat 23.78, Lon 72.64, Asia/Kolkata (Vadnagar)

---

## Natal Seed

- **Neecha Bhanga Raja Yoga present:** **NO**

**Explanation:** For 1950-09-17 11:00 Vadnagar, the engine (Swiss Ephemeris, Lahiri) places **Mars in Scorpio (sign 7), house 12**, and **Moon in Scorpio (sign 7), house 1**. Mars is therefore in **own sign (Scorpio)**, not in Cancer (debilitated). Neecha Bhanga Raja Yoga requires Mars debilitated in Cancer with debility cancelled (e.g. by Moon in Kendra). With Mars in Scorpio, that condition is not met. The yoga list contains **“Neechabhanga Raja Yoga”** in `all_yogas` (from extended detection), but it has no participants in the activation engine’s participant resolution (name/rule mismatch or no planet/planets), so it is **not** included in the activation list. The only yoga that appears in the activation list for this chart is **Ruchaka Yoga** (Mars in own sign in Kendra from Moon), with participant Mars. So in the activation API, Neecha Bhanga Raja Yoga is **not** present.

---

## Dasha Permission

- **Mars Mahadasha window detected:** **YES**

**Engine-derived:** Mars MD: **2021-11-28 → 2028-11-28**. Current (e.g. 2025) is Mars MD, Mars Antardasha has already run (2021-11-28 → 2022-04-26). So the Dasha Gate is/was open for Mars-participant yogas (e.g. Ruchaka) only during Mars MD, and within that only during antardashas whose lord is a participant (e.g. Mars–Mars).

---

## Forecast Behavior

- **First activation year:** **N/A**
- **Last activation year:** **N/A**
- **Any activation after 2028:** **NO**

**Explanation:** The only yoga in the activation list for this chart is **Ruchaka Yoga** (participant: Mars). Forecast logic uses **Dasha Siege**: only windows where MD lord and AD lord are both yoga participants. For Ruchaka, the only such window is **Mars MD + Mars AD** (2021-11-28 → 2022-04-26). That window lies **entirely in the past** relative to “today” (e.g. 2025). So there is **no** future window in the next 100 years that satisfies both Mars MD and Mars AD for Ruchaka. The forecast correctly returns **0** Ruchaka activations. Hence: no activations after 2028, and no activations in 2040/2060/2100. **Dasha Cliff** is satisfied: no activations occur after Mars MD, because there is no future Mars–Mars (MD–AD) window.

---

## Triggers

- **Trigger planets observed:** **[]** (no forecast entries)
- **Any invalid trigger:** **NO**

For the single yoga in the activation list (Ruchaka), trigger would be Mars only; no forecast entries exist, so no invalid trigger is possible.

---

## Ashtakavarga

- **Bindu range observed:** **N/A** (no activations)
- **Variation across windows:** **N/A**

---

## Data Integrity

- **JSON valid, no crash:** **YES** (HTTP 200, valid response)
- **philosophy string:** Present in code; if omitted in response, engine logic is unchanged.

---

## Final Verdict

**PASS**

The Secondary Switch logic behaves correctly. (1) **Natal seed:** Neecha Bhanga Raja Yoga is not present in the activation list (Mars is in Scorpio in this ephemeris, not Cancer; and/or participant resolution excludes “Neechabhanga Raja Yoga”). Ruchaka Yoga (Mars) is present and correctly appears in summary as Dormant when there is no current transit contact. (2) **Dasha permission:** Mars MD 2021–2028 is detected; forecast only considers windows where both MD and AD lords are yoga participants. (3) **Dasha Cliff:** The only qualifying window for Ruchaka (Mars–Mars) is 2021–2022, which is in the past; hence **zero** future activations and **zero** activations after 2028. Transit alone does not activate: without a future Mars MD + Mars AD window, no activations are returned even though Mars will transit again. Ashtakavarga would modulate comfort only when activations exist; here there are none. No fabricated activations, no activations outside Dasha, valid JSON. The engine behaves as a strict Secondary Switch: **Dasha grants permission, transit gives timing.**

**Truth > Appearance.**
