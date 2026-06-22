# LOAM — Bijbel Index
*Altijd hier starten. Nooit een sub-document raadplegen zonder via de index te gaan.*

---

## Premise

**2047. Een stad zonder naam. Een wereld die niet brak maar uitputte.**

The Contraction (2031–2039) vernielde niets in één klap — het liet alles langzaam leeglopen. AI nam het werk. Populisme vergiftigde de samenwerking. Klimaat verschoof, oogsten faalden, pensioenen knakten. The Accord werd in 2036 ingezet als noodmaatregel en nooit meer uitgezet. Het optimaliseert. Het duurt. Het is geduldig op een manier die mensen niet zijn.

In een afgeschreven spoorwegterrein in Sector 9 houdt een man iets in leven dat officieel niet meer bestaat.

Een vrouw vindt hem.

---

## De wet van dit verhaal

- Het mag pijn doen. Het moet soms verscheuren.
- Warmte wordt alleen toegelaten als ze bevochten is.
- Elias is niet lief. Mara is niet onschuldig.
- The Accord wint niet dramatisch — het slijt.
- Hoop is een zaad. Het kan sterven.

---

## Personages

| Naam | Status | Bestand | Laatste verschijning |
|------|--------|---------|----------------------|
| Elias Voss | actief — in de tuin | [elias.md](personages/elias.md) | dag 036 |
| Mara | actief — document verstuurd, Elias op de hoogte | [mara.md](personages/mara.md) | dag 035 |
| Lena Voss | afwezig — nog niet in verhaal | [lena.md](personages/lena.md) | — (gepland ~dag 050) |

---

## Locaties

| Naam | Status | Bestand | Laatste vermelding |
|------|--------|---------|-------------------|
| De Tuin | actief — open lucht, spoorwegterrein | [de-tuin.md](locaties/de-tuin.md) | dag 032 |
| De Stad | achtergrond | [de-stad.md](locaties/de-stad.md) | dag 025 |
| Sector 9 | escalerend — ZVA voltooid | [sector-9.md](locaties/sector-9.md) | dag 029 |

---

## Intriges

| Naam | Fase | Bestand |
|------|------|---------|
| The Accord — wat schuift er? | 💧 sluimerend | [the-accord.md](intriges/the-accord.md) |
| Lena — waar is ze? | 🌱 geplant | [lena-voss.md](intriges/lena-voss.md) |
| Mara — gestuurd of gevonden? | 🌱 geplant | [mara-gestuurd.md](intriges/mara-gestuurd.md) |
| Elias — wat heeft hij gedaan? | 💧 sluimerend | [elias-verleden.md](intriges/elias-verleden.md) |

Fasen: 🌱 geplant / 💧 sluimerend / 🔥 escalerend / 💥 climax / 🍂 resolutie

---

## Publicatieworkflow

### Schrijven (per batch van 7)
1. Claude schrijft 7 fragmenten in één sessie — met geplande bogen over de hele batch
2. Elk fragment opslaan als `bijbel/fragmenten/drafts/dag-XXX.md` met frontmatter:
   ```
   ---
   dag: 001
   deploy_date: 2026-07-01
   story_date: "March 15, 2047"
   status: draft
   ---
   ```
3. Peter verwittigen via Telegram: "LOAM — Batch DAG XXX–XXX klaar voor proeflezen"
4. Volledige tekst van elke fragment in aparte Telegram-berichten

### Valideren
- Peter leest in eigen tempo — kan week(en) voor zijn op publicatie
- Taalcorrecties doorsturen of gewoon "ok" per fragment
- Na goedkeuring: status `draft` → `scheduled`, bestand verplaatst naar `bijbel/fragmenten/`

### Publiceren (automatisch)
- GitHub Actions draait dagelijks om 07:00
- Checkt welke fragmenten `deploy_date <= vandaag` hebben
- Rebuildt de statische site met die fragmenten
- Pusht naar `gh-pages` branch

### Buffer-doel
Altijd minimum 7 gevalideerde fragmenten in de pipeline. Als de buffer onder de 7 zakt: nieuwe batch schrijven.

---

## Stijlgids

- **Perspectief:** derde persoon beperkt — primair Mara, occasioneel Elias
- **Tijd:** tegenwoordige tijd (present tense)
- **Ritme:** korte zinnen bij spanning, langere zinnen in de tuin
- **The Accord:** verschijnt als opgemaakte systeemblokken — nooit als stem, nooit als karakter
- **Fragmentnummering:** DAG-001, DAG-002 — geen titels, wel een datumregel in de story-world
- **Wat vermijden:** heldenmoed, verlossing, toespraken over vrijheid
- **Taal consistentie:** alle namen — personen, straten, plaatsen — zijn Engelstalig. Geen Nederlandse, Belgische of andere niet-Engelstalige namen invoeren. (Fout: Geert, Tierstraat. Goed: Owen, Meridian Street.)

---

## Dagelijkse briefing

→ [stand.md](stand.md)

---

## Tijdlijn

→ [tijdlijn.md](tijdlijn.md)
