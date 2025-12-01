"""
SPARQL query templates for fetching narrative-related entities from Wikidata.

We target three roots:

- Q212806   : literary archetype
- Q13055555 : science fiction theme
- Q46996652 : video game mechanic

For each entity we try to fetch:
- label (English)
- description (English)
- ATU index (P2540) if present
- linked English Wikipedia sitelink (title)
"""

LITERARY_ARCHETYPE_QID = "Q212806"
SCIFI_THEME_QID = "Q13055555"
VIDEOGAME_MECHANIC_QID = "Q46996652"


def make_root_query(root_qid: str, limit: int | None = None) -> str:
    """
    Broader query to capture narrative entities.

    It finds entities that are:
    - instance of the root
    - subclass of the root
    - have genre P136 equal to root (common for narrative concepts)
    - have main subject P921 equal to root
    """

    limit_clause = f"LIMIT {int(limit)}" if limit is not None else ""

    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX schema: <http://schema.org/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX bd: <http://www.bigdata.com/rdf#>

    SELECT ?entity ?entityLabel ?entityDescription ?atu ?wikipediaTitle
    WHERE {{
      VALUES ?root {{ wd:{root_qid} }}

      # Match broader narrative relationships
      ?entity wdt:P31|wdt:P279|wdt:P136|wdt:P921 ?root .

      OPTIONAL {{ ?entity wdt:P2540 ?atu . }}

      OPTIONAL {{
        ?sitelink schema:about ?entity ;
                  schema:isPartOf <https://en.wikipedia.org/> ;
                  schema:name ?wikipediaTitle .
      }}

      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en" .
      }}
    }}
    {limit_clause}
    """

    return query.strip()