# sparl-test
This directory contains sample code accessing and playing around with different wikidata services.

Specifically, there are examples of using:
- `sparql`
- `searching for entity id based on entity name`
- `searching for property id based on property name`

These 3 should be enough to make a simple fact checking algorithm. For example, the user may input a fact to the LLM. Then, the LLM can dissect that fact into a semantic triple. Then, the LLM can perform an entity search based on the first entity, and a property search. Then, I can do a SPARQL query with these 2 values to fetch the third value, since the third value might not necessarily be an entity with an ID. It could just be an arbitrary value like `20cm`. It could be an entity as well, but as long as I have the first 2, I can fetch the third value, and then just use the LLM to compare the values.

This is because the first entity is what I like to think of as the primary entity. It is the webpage that you go on to find the information about said person.

For example, I can have "Lebron James, height, 206 cm"

The first entity/primary would be Lebron James. I would go to his page to find out he is 206 cm.

Here is an example query:
```
SELECT ?height
WHERE {
    wd:Q36159 wdt:P2048 ?height .
}
LIMIT 10
```
`wd:Q36159`: Lebron James
`wdt:P2048`: height
`?height`: variable name thats called `height`, where we store the third entity of the semantic triple in.

This basically gets the height of Lebron James, and limits it to 10 values (since relationships are has- relationships, so its possible for some properties to have multiple values, like `children`).