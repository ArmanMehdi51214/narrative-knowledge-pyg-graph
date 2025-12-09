"""
nomenclature_builder.py

Builds the nomenclature.json file required by the client.
Each "culture" contains:
- id
- optional source_entity (QID)
- male_names
- female_names
- place_names

Names may come from:
1) Wikidata queries (preferred)
2) Local fallback lists

The final JSON matches the required schema:

{
  "meta": {"version": "1.0"},
  "cultures": [
      {
        "id": "culture_nordic_ice",
        "source_entity": "Q12345",
        "male_names": [...],
        "female_names": [...],
        "place_names": [...]
      }
  ]
}
"""
 # Ensure local imports work when run as script

from __future__ import annotations
import json
import logging
from typing import List, Dict, Optional

from wd_api.wikidata_client import WikidataClient  # your existing client


logger = logging.getLogger(__name__
                           )


class NomenclatureBuilder:

    def __init__(self, output_path: str = "nomenclature.json"):
        self.output_path = output_path
        self.wd = WikidataClient()

    # ---------------------------------------------------------------------
    # Wikidata Query Helpers
    # ---------------------------------------------------------------------

    def fetch_person_names(self, qid: str, limit: int = 200) -> List[str]:
        """
        Fetch given names from a Wikidata category/entity.

        Returns a list of labels only.
        """
        query = f"""
        SELECT ?name ?nameLabel WHERE {{
          ?name wdt:P31 wd:Q202444 .      # instance of: given name
          ?name wdt:P910 ?cat .           # category
          FILTER(?cat = wd:{qid})

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """

        try:
            data = self.wd.run_sparql(query)
        except Exception as e:
            logger.error(f"Wikidata fetch failed for QID {qid}: {e}")
            return []

        names = []
        for row in data.get("results", {}).get("bindings", []):
            label = row.get("nameLabel", {}).get("value")
            if label:
                names.append(label)

        return names

    def fetch_place_names(self, qid: str, limit: int = 200) -> List[str]:
        """
        Fetch place names related to a Wikidata cultural region.
        """
        query = f"""
        SELECT ?place ?placeLabel WHERE {{
          ?place wdt:P31/wdt:P279* wd:Q486972 .  # instance of or subclass: human settlement
          ?place wdt:P361 wd:{qid} .              # part_of the cultural region

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """

        try:
            data = self.wd.run_sparql(query)
        except Exception as e:
            logger.error(f"Wikidata place fetch failed for QID {qid}: {e}")
            return []

        places = []
        for row in data.get("results", {}).get("bindings", []):
            label = row.get("placeLabel", {}).get("value")
            if label:
                places.append(label)

        return places

    # ---------------------------------------------------------------------
    # Culture Builder
    # ---------------------------------------------------------------------

    def build_culture(
        self,
        culture_id: str,
        source_qid: Optional[str],
        fallback_male: List[str],
        fallback_female: List[str],
        fallback_places: List[str],
        enable_wikidata: bool = True
    ) -> Dict:
        """
        Construct one culture entry.

        If enable_wikidata=False, we only use fallback lists.
        """

        male = list(fallback_male)
        female = list(fallback_female)
        places = list(fallback_places)

        if enable_wikidata and source_qid:
            # Try name enrichment
            try:
                male += self.fetch_person_names(source_qid)
                female += self.fetch_person_names(source_qid)
                places += self.fetch_place_names(source_qid)
            except Exception as e:
                logger.error(f"Error during Wikidata enrichment for {culture_id}: {e}")

        # Deduplicate
        male = sorted(list(set(male)))
        female = sorted(list(set(female)))
        places = sorted(list(set(places)))

        return {
            "id": culture_id,
            "source_entity": source_qid,
            "male_names": male,
            "female_names": female,
            "place_names": places
        }

    # ---------------------------------------------------------------------
    # Full build
    # ---------------------------------------------------------------------

    def build_and_save(self, enable_wikidata: bool = True):
        """
        Build all cultures and save nomenclature.json
        """

        cultures = []

        # ------------------------------------------------------------
        # CULTURE 1: Old Norse / Ice Faction
        # ------------------------------------------------------------
        cultures.append(
            self.build_culture(
                culture_id="culture_nordic_ice",
                source_qid="Q8458",  # Norse mythology
                fallback_male=["Erik", "Bjorn", "Leif", "Torsten"],
                fallback_female=["Freya", "Sif", "Astrid"],
                fallback_places=["Frosthold", "Winterdeep"],
                enable_wikidata=enable_wikidata
            )
        )

        # ------------------------------------------------------------
        # CULTURE 2: Roman / Latin
        # ------------------------------------------------------------
        cultures.append(
            self.build_culture(
                culture_id="culture_roman_imperial",
                source_qid="Q211062",  # Roman mythology
                fallback_male=["Marcus", "Lucius", "Gaius"],
                fallback_female=["Julia", "Livia", "Aurelia"],
                fallback_places=["Imperium", "Solarum"],
                enable_wikidata=enable_wikidata
            )
        )

        # ------------------------------------------------------------
        # CULTURE 3: Hebrew / Biblical
        # ------------------------------------------------------------
        cultures.append(
            self.build_culture(
                culture_id="culture_hebrew_cult",
                source_qid="Q1845",  # Hebrew Bible
                fallback_male=["Eli", "David", "Amos"],
                fallback_female=["Miriam", "Hannah", "Naomi"],
                fallback_places=["Zeruel", "Ashdod"],
                enable_wikidata=enable_wikidata
            )
        )

        # ------------------------------------------------------------
        # CULTURE 4: Japanese / Cyberpunk
        # ------------------------------------------------------------
        cultures.append(
            self.build_culture(
                culture_id="culture_cyber_high_tech",
                source_qid="Q5287",  # Japanese language / names category proxy
                fallback_male=["Neo", "Glitch", "Cipher"],
                fallback_female=["Rei", "Kira", "Aya"],
                fallback_places=["Neotokyo", "Chrome District"],
                enable_wikidata=enable_wikidata
            )
        )

        # ------------------------------------------------------------
        # CULTURE 5: Geological / Industrial (Robot/AI)
        # ------------------------------------------------------------
        cultures.append(
            self.build_culture(
                culture_id="culture_industrial_mech",
                source_qid="Q214609",  # geology
                fallback_male=["Ferron", "Granite", "Cobalt"],
                fallback_female=["Quartz", "Beryl"],
                fallback_places=["Ironhaven", "Cobalt Ridge"],
                enable_wikidata=enable_wikidata
            )
        )

        # ------------------------------------------------------------
        # Final JSON assembly
        # ------------------------------------------------------------

        output = {
            "meta": {"version": "1.0"},
            "cultures": cultures
        }

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Nomenclature saved → {self.output_path}")
        return output


# ---------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    builder = NomenclatureBuilder(output_path="nomenclature.json")
    builder.build_and_save(enable_wikidata=False)  # set True to use real Wikidata
