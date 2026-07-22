# LOAM — Bijbel Index
*Altijd hier starten. Nooit een sub-document raadplegen zonder via de index te gaan.*

---

## Premise

**2047. Een stad zonder naam. Een wereld die niet brak maar uitputte.**

The Contraction (2031–2039) vernielde niets in één klap — het liet alles langzaam leeglopen. AI nam het werk. Populisme vergiftigde de samenwerking. Klimaat verschoof, oogsten faalden, pensioenen knakten. The Accord werd in 2036 ingezet als noodmaatregel en nooit meer uitgezet. Het optimaliseert. Het duurt. Het is geduldig op een manier die mensen niet zijn.

In een afgeschreven spoorwegterrein in Sector 9 houdt een man iets in leven dat officieel niet meer bestaat.

Een vrouw vindt hem.

---

## Status van het verhaal

**Het volledige verhaal (dag 1-95) is geschreven.** Dag 001-038 zijn `scheduled` en live op readloam.com. Dag 039-095 staan als `draft` in `bijbel/fragmenten/drafts/`, wachtend op Peters proeflezing/validatie (zie Publicatieworkflow hieronder). Alle tabellen op deze pagina reflecteren de volledige tekst, inclusief drafts — waar relevant staat het dagnummer waarop iets nog draft is expliciet vermeld.

Voor een volledige samenvatting van fase 3-5 (het draft-gedeelte) en een lijst van bewust open gelaten keuzes: zie [stand.md](stand.md).

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
| Elias Voss | (draft) tuin gesloopt dag 93-94; in kankerbehandeling; slotbeeld dag 95 | [elias.md](personages/elias.md) | dag 095 (draft) |
| Mara | (draft) verloor toegang tot Sector 9-data (dag 86); weet nu van Lena | [mara.md](personages/mara.md) | dag 095 (draft) |
| Daniel | (draft) buurtbewoner Block 4, nieuw sinds dag 43 — bezwaarschrift gedeeltelijk gewonnen (dag 81) | *(geen eigen bestand — zie elias.md/ARC.md)* | dag 093 (draft) |
| Lena Voss | (draft) nog niet fysiek verschenen — genoemd dag 50 (data), 85 (onthulling aan Mara), 91 (pakketje afgeleverd, geen reactie) | [lena.md](personages/lena.md) | — (nooit fysiek in beeld; bewust) |

---

## Locaties

| Naam | Status | Bestand | Laatste vermelding |
|------|--------|---------|-------------------|
| De Tuin | (draft) **gesloopt dag 93-94** — bestaat niet meer | [de-tuin.md](locaties/de-tuin.md) | dag 095 (draft) |
| De Stad | achtergrond | [de-stad.md](locaties/de-stad.md) | dag 025 |
| Sector 9 | (draft) remediatie voltrokken — zie De Tuin | [sector-9.md](locaties/sector-9.md) | dag 093 (draft) |

---

## Intriges

| Naam | Fase | Bestand |
|------|------|---------|
| The Accord — wat schuift er? (de micro-anomalie) | 💧 sluimerend — **nooit geplant binnen dag 1-95, losse draad** | [the-accord.md](intriges/the-accord.md) |
| Lena — waar is ze? | 🍂 resolutie (draft, dag 84-91) — Elias' kant afgehandeld, Lena's reactie bewust onopgelost | [lena-voss.md](intriges/lena-voss.md) |
| Mara — gestuurd of gevonden? | 🍂 resolutie (draft, dag 57-59) — vraag gesteld en confronterend, bewust nooit beantwoord | [mara-gestuurd.md](intriges/mara-gestuurd.md) |
| Elias — wat heeft hij gedaan? | 🍂 resolutie (draft) — vrijwel alles onthuld aan Mara, incl. Lena (dag 85) | [elias-verleden.md](intriges/elias-verleden.md) |

Fasen: 🌱 geplant / 💧 sluimerend / 🔥 escalerend / 💥 climax / 🍂 resolutie

**Let op:** de Accord-micro-anomalie ("wat schuift er in de architectuur") is de enige intrige uit de oorspronkelijke bijbel die nooit is geplant binnen de geschreven 95 dagen — `stand.md` bleef hem het hele verhaal door als "nog niet geplant" vermelden. Dit is een bewuste, expliciete lacune, geen fout: de lange boog die `intriges/the-accord.md` beschrijft ("dit is de climax van seizoen 1") past niet meer binnen dag 1-95 zoals het verhaal zich ontwikkeld heeft. Peter kan beslissen of dit losse eind blijft liggen (een verhaal mag onbeantwoorde vragen hebben) of dat het alsnog een plek moet krijgen bij het herzien van de drafts.

---

## Publicatieworkflow

### Schrijven (per batch van 7)
1. Claude schrijft 7 fragmenten in één sessie — met geplande bogen over de hele batch
2. Elk fragment opslaan als `bijbel/fragmenten/drafts/0XX.md` (drie cijfers, geen "dag-"-prefix — zie `scripts/loam-schrijver-prompt.md`) met frontmatter:
   ```
   ---
   day: 39
   deploy_date: 2026-07-25
   story_date: "April 20, 2047"
   status: draft
   ---
   ```
   Let op: het frontmatter-veld heet `day`, niet `dag` — dit werd hier eerder verkeerd gedocumenteerd.
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
