import logging
from wd_api.wikidata_client import WikidataClient
from wiki_api.wikipedia_client import WikipediaClient

logging.basicConfig(level=logging.INFO)

wd = WikidataClient()
wiki = WikipediaClient()

print("\n=== TEST 1: Fetch 5 ATU Folktales ===")

query = """
SELECT ?entity ?entityLabel ?entityDescription ?atu ?wikipediaTitle WHERE {
  ?entity wdt:P2540 ?atu .

  OPTIONAL {
    ?sitelink schema:about ?entity ;
              schema:isPartOf <https://en.wikipedia.org/> ;
              schema:name ?wikipediaTitle .
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 5
"""

results = wd.run_sparql(query)["results"]["bindings"]

for row in results:
    print(row)

# Now try fetching summary for the first item that has a Wikipedia title
w_title = None
for row in results:
    if "wikipediaTitle" in row:
        w_title = row["wikipediaTitle"]["value"]
        break

print("\n=== TEST 2: Wikipedia Summary ===")

if w_title:
    summary = wiki.fetch_summary(w_title)
    print(summary)
else:
    print("No Wikipedia-linked tales in this batch.")
