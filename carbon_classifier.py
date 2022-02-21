import json
import os
import random

import numpy as np
import pandas as pd
import requests
import spacy
from fuzzywuzzy import fuzz

from firestore_helper import write_to_reported


class MatchedCategory:
    def __init__(self, original, matched, alternatives, log_id):
        self.original = original
        self.matched = matched
        self.alternatives = alternatives
        self.log_id = log_id


def find_exact_match(ingredient, carbon_categories):
    found = False
    match_category = ""

    for carbon_category in carbon_categories:
        if ingredient in carbon_categories[carbon_category]:
            found = True
            match_category = carbon_category
            print(f"match_category: {match_category}")

    return found, match_category


def find_fuzzy_match(ingredient, carbon_categories):

    found = False
    match_category = False
    threshold = 80

    similarity_df = pd.DataFrame({"category": [], "match": [], "match_rate": []})

    # fuzz.partial_ratio("tomato", "tomatoes")

    for i, carbon_category in enumerate(carbon_categories):
        fuzzy_similarities = []
        for category_syn in carbon_categories[carbon_category]:
            fuzzy_similarity = fuzz.ratio(ingredient, category_syn)
            fuzzy_similarities.append(fuzzy_similarity)

        fuzzy_similarities = pd.Series(fuzzy_similarities)
        max_similarity_id = fuzzy_similarities.idxmax()
        max_similarity = fuzzy_similarities.max()

        similarity_df.loc[i] = [
            carbon_category,
            carbon_categories[carbon_category][max_similarity_id],
            max_similarity,
        ]

    max_similarity_rate = similarity_df["match_rate"].max()
    max_similarity_id = similarity_df["match_rate"].idxmax()
    max_similarity_df = similarity_df.loc[max_similarity_id]

    if max_similarity_rate > threshold:
        found = True
        match_category = max_similarity_df["category"]

    return found, match_category


def find_rule_matches(ingredient):
    found = False
    match_category = False
    if ingredient == "mince":
        match_category = "beef"

    if match_category != False:
        found = True

    return found, match_category



def get_carbon_cat(ingredient, carbon_categories, all_alternatives):

    ingredient = ingredient.lower()

    print(f"categorising: {ingredient}")
    found = False
    category_match = ""

    # test for exact matches
    found, category_match = find_exact_match(ingredient, carbon_categories)

    # test for rule matches
    if found == False:
        found, category_match = find_rule_matches(ingredient)

    # then test for fuzzy matches
    if found == False:
        found, category_match = find_fuzzy_match(ingredient, carbon_categories)

    # # if semantic flag enabled
    if found == False and os.getenv("USE_SEMANTIC_SERVICE") == "True":
        # # test for semantic matches
        x = requests.post(os.getenv("SEMANTIC_SERVICE_URI"), json={"name": ingredient})
        response = json.loads(x.text)
        if response["found"]:
            category_match = response["matched"]
            found = True

    alternatives = []

    if found == False:
        category_match = "misc"
    else:
        alternatives = all_alternatives[category_match]

    # report
    log_id = random.randint(9999, 99999)

    write_to_reported(log_id, category_match, ingredient)

    return vars(MatchedCategory(ingredient, category_match, alternatives, log_id))


def get_carbon_categories(ingredients, carbon_categories, all_alternatives):
    ingredient_output = []

    for ingredient in ingredients:
        ingredient_output.append(get_carbon_cat(ingredient, carbon_categories, all_alternatives))

    return ingredient_output
