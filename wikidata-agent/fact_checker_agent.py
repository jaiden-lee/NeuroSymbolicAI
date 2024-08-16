from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import re
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests
import chromadb

class FactCheckerAgent:
    def __init__(self):
        # Load the model
        model_name = "bartowski/Mistral-7B-Instruct-v0.3-GGUF"
        model_file = "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
        model_path = hf_hub_download(model_name, filename=model_file)
        self.model = Llama(
            model_path = model_path,
            n_ctx=32000,
            verbose=False
        )

        # Define system prompt
        self.system_prompt = """
You will first be given a fact by the user, and your goal is to determine whether or not that fact is true or false.

You have only 2 jobs:
1) Search wikidata by outputting a semantic triple
2) Answer the user

Your response must always include a THOUGHT and a RESPONSE keyword, and then you must follow it with the PAUSE keyword.

If you decide that you need more information do determine whether a fact is true, then you can perform a search on wikidata. To do this, you need to output a semantic triple, which follows the format: ENTITY_1 RELATIONSHIP ENTITY_2.

Specifically, I want you to output the JSON: 
RESPONSE: {"entity_1": "entity1", "relationship": "relationship", "entity_2": "entity2"}

If you decide that you do not need more information, and can say whether a fact is true or false, then simply output the JSON:
RESPONSE: {"message": "Whether the fact is true/false, and your reasoning."}

If you decide to call wikidata, you will be provided the result of the query ENTITY_1 ", which will be the true value for ENTITY_2. Then, you will compare the true value for ENTITY_2 to your predicted value for ENTITY_2.

###EXAMPLE 1:
User: Bach was a composer.

THOUGHT: I assume the user is talking about the musician Johann Bach. I will perform a search on wikidata.
RESPONSE: {"entity_1": "Johann Bach", "relationship": "occupation", "entity_2": "composer"}
PAUSE

RESULT: ["composer", "musician", "organist", "violinist", ...]

THOUGHT: I have enough information now.
RESPONSE: {"message": "True. According to wikidata, one of the many occupations Bach had was a composer."}
PAUSE
###END EXAMPLE 1

###EXAMPLE 2:
User: Lebron James was born in the United States.

THOUGHT: I will look up where Lebron James was born.
RESPONSE: {"entity_1": "Lebron James", "relationship": "place of birth", "entity_2": "United States"}
PAUSE

RESULT: "Akron"

THOUGHT: Since Akron is a city, I should find what country Akron is located in.
RESPONSE: {"entity_1": "Akron", "relationship": "country", "entity_2": "United States"}
PAUSE

RESULT: "United States"

THOUGHT: I have enough information to answer the user now.
RESPONSE: {"message": "True. Lebron James was born in Akron, which is a city in the United States."}
PAUSE
###END EXAMPLE 2

###EXAMPLE 3:
User: Lebron James has 4 children.

THOUGHT: Number of children is most likely not a property in wikidata, but children is. I will first find all of Lebron Jame"s children, then count the number of children he has. I can leave the 2nd entity empty since I don"t care about it.
RESPONSE: {"entity_1": "Lebron James", "relationship": "children", "entity_2": ""}
PAUSE

RESULT: ["Bryce James", "Bronny James", "Zhuri James"]

THOUGHT: By counting the result, I can tell that Lebron has 3 children, not 4
RESPONSE: {"message": "False. Lebron James has 3 children: Bryce, Bronny, and Zhuri."}
PAUSE
###END EXAMPLE 3
""".strip()
        self.relationship_verification_prompt = """
You are an AI assistant with 1 job: verify if 2 relationships are semantically the same.

You will be provided with a semantic triple (which contains an entity_1, relationship, and entity_2), as well as a Task, and a predicted relationship.

Your goal is to output True/False depending on if the predicted relationship would is semantically the same as the relationship in the semantic triple.

###EXAMPLE 1:
Task: I will look up where Lebron James was born.
Semantic triple: {"entity_1": "Lebron James", "relationship": "birthplace", "entity_2": "United States"}
Relationship: place of birth

THOUGHT: birthplace is the same as place of birth
RESPONSE: True
PAUSE
###END EXAMPLE 1

###EXAMPLE 2:
Task: Since Akron is a city, I should find what country Akron is located in.
Semantic triple: {"entity_1": "Akron", "relationship": "country", "entity_2": "United States"}
Relationship: Parent nation

THOUGHT: parent nation is most likely semantically the same as country
RESPONSE: True
PAUSE
###END EXAMPLE 2

###EXAMPLE 3
Task: I will look up to see if the etruscan shrew is the smallest mammal on the planet.
Semantic triple: {"entity_1": "earth", "relationship": "smallest", entity_2: "Etruscan Shrew"}
Relationship: size

THOUGHT: size is most likely not referring to the smallest mammal
RESPONSE: False
PAUSE
###END EXAMPLE 3
"""
        # Create DB to use for RAG to select relationship
        self.relationship_db = chromadb.Client()

        # Wikidata API setup
        self.wikidata_api_endpoint = "https://www.wikidata.org/w/api.php"
        wikidata_sparql_endpoint = "https://query.wikidata.org/sparql"
        self.sparql = SPARQLWrapper(wikidata_sparql_endpoint)
        self.sparql.setReturnFormat(JSON)

    def query(self, query, verbose = False):
        # defining the prompt to feed the model
        prompt = f"""
[SYSTEM]
{self.system_prompt}

[USER]
{query}

[ASSISTANT]
THOUGHT:
""".strip()
        for _ in range(10):
            
            # prints out the current iteration
            if verbose:
                print(f"________________________ITERATION: {_+1}________________________")
                print(prompt)

            # The model output
            output = self.model(
                prompt=prompt,
                stop=["PAUSE"],
                max_tokens=512
            )["choices"][0]["text"]

            # Parsing the output string
            response_regex = "RESPONSE: (.*)"
            foundResponse = re.search(response_regex, output)

            if foundResponse: # RESPONSE keyword and JSON object has been found
                response_json = {}
                
                # turns JSON into python dict or handles failed case
                try:
                    response_json = json.loads(foundResponse.group(1))
                except:
                    if verbose:
                        print("ERROR: JSON could not be parsed")
                        print("Here is the bad output:")
                        print(output)
                    continue # if the json can't be parsed, the model produced a bad output, so we regenerate the output
                
                # message keyword found, means that model is done analyzing and produced final answer
                if "message" in response_json:
                    return response_json["message"]
                # this means a triple was produced instead
                elif "entity_1" in response_json and "relationship" in response_json:
                    prompt += f"{output}\nPAUSE\n"

                    if verbose:
                        print("Successful output:")
                        print(output)

                    entity_1 = response_json["entity_1"]
                    relationship = response_json["relationship"]
                    thought = output.split("\n")[0]

                    # look for the id of entity from wikidata via API search
                    parameters = {
                        "action":"wbsearchentities",
                        "search":entity_1,
                        "language":"en",
                        "type":"item",
                        "format":"json"
                    }
                    entity_response = requests.get(self.wikidata_api_endpoint, params=parameters)

                    # if status code is in 400 range
                    if entity_response.status_code//100 == 4:
                        if verbose:
                            print("Wikidata API call not working, cannot proceed with fact checking")
                        return "Could not check fact due to API failure"
                    
                    matching_entities_list = entity_response.json()["search"]

                    if len(matching_entities_list) == 0:
                        if verbose:
                            print(f"Wikidata has no entities called {entity_1}")
                        prompt+=f"RESULT: Wikidata has no entities called {entity_1}\n\nTHOUGHT:"
                        continue
                    # for now, select the first result from wikidata since its most likely the one we are talking about
                    top_result = matching_entities_list[0]
                    entity_id = top_result["id"]
                    if verbose:
                        print("Here are all the matching entities:")
                        print(matching_entities_list)

                    # Create a RAG collection to store relationships in
                    collection = None
                    try: # collection already exists
                        collection = self.relationship_db.get_collection(entity_id)
                        if collection.count() == 0: # most likely means we failed to add docs last time we ran, so rerun
                            raise RuntimeError("Collection exists, but no docs") # forces us to recreate collection
                    except: # if collection doesn't exist, we need to create it    
                        # Retrieve all relationships in entity_1
                        self.sparql.setQuery("""
SELECT ?property ?propertyLabel WHERE {
wd:"""+entity_id+""" ?directClaim ?object .
?property wikibase:directClaim ?directClaim .
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
""")
                        relationships_unformatted = []
                        try:
                            relationships_result = self.sparql.query().convert() 
                            relationships_unformatted = relationships_result["results"]["bindings"]
                        except:
                            if verbose:
                                print("SPARQL query failed: Could not fetch the list of relationships")
                                return "Could not fact check due to SPARQL Query failure"
                            
                        # Converting relationships into a dictionary(name -> id) and ids, names array for RAG
                        relationships = {}
                        ids = []
                        names = []
                        for prop in relationships_unformatted:
                            property_id = prop["property"]["value"][prop["property"]["value"].index("P"):]
                            property_name = prop["propertyLabel"]["value"]
                            if property_name not in relationships:
                                ids.append(property_id)
                                names.append(property_name)
                            relationships[property_name] = property_id

                        if verbose:
                            print("Here is a list of all relationships the entity has:")
                            print(relationships)

                        collection = self.relationship_db.get_or_create_collection(entity_id)
                        collection.add(documents=names, ids=ids)

                    # Use vector search to find which property to use
                    relationship_doc = collection.query(query_texts=relationship, n_results=1)
                    relationship_id = relationship_doc["ids"][0][0]

                    verify_prompt = f"""
[SYSTEM]
{self.relationship_verification_prompt}

[USER]
Task: {thought}
Semantic Triple: {response_json}
Relationship: {relationship_doc['documents'][0][0]}

THOUGHT:
"""
                    verify_output = self.model(
                        prompt=verify_prompt,
                        stop=["PAUSE"],
                        max_tokens=512
                    )["choices"][0]["text"]

                    if verbose:
                        print("Verification output")
                        print(verify_output)
                    if ("False" in verify_output):
                        prompt+="RESULT: Relationship not found, please try a different relationship.\n\nTHOUGHT:"
                        if verbose:
                            print("Relationship did not match")
                        continue

                    # NOTE: need to handle case where the relationship selected is different from the relationship we predicted (aka, that relationship could not be found in the entity)

                    if verbose:
                        print("Here is the relationship selected:")
                        print(relationship_id, relationship_doc["documents"][0][0])   

                    # Fetch the real value for entity_3
                    self.sparql.setQuery("""
SELECT ?value ?valueLabel WHERE {
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    wd:"""+entity_id+""" wdt:"""+relationship_id+""" ?value .
}
""")
                    entity_2_results = self.sparql.query().convert()
                    entity_2_values = entity_2_results["results"]["bindings"]
                    
                    entity_2_values_formatted = []

                    for value in entity_2_values:
                        entity_2_values_formatted.append(value["valueLabel"]["value"])

                    if verbose:
                        print("Here are all the values associated with the selected relationship")
                        print(entity_2_values_formatted)
                    
                    prompt+=f"RESULT: {entity_2_values_formatted}\n\nTHOUGHT:"
                    
            

            else: # RESPONSE keyword not found, so restart
                if verbose:
                    print("ERROR: RESPONSE keyword not found")
                    print("Here is the bad output")
                    print(output)
        return "Fact could not be verified"