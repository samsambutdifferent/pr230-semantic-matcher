import pandas as pd
import numpy as np
import os
import spacy
from fuzzywuzzy import fuzz
from firestore_helper import load_carbon_matches
from helper import log_match
import requests
import json

nlp = spacy.load("en_core_web_lg")

class MatchedCategory:
  def __init__(self, original, matched, log_id):
    self.original = original
    self.matched = matched
    self.log_id = log_id

def find_exact_match(ingredient, carbon_categories):
    found = False
    match_category = ''

    for carbon_category in carbon_categories: 
        if ingredient in carbon_categories[carbon_category]:
            found = True
            match_category = carbon_category
    
    return found, match_category


def find_fuzzy_match(ingredient, carbon_categories):
    
    found = False 
    match_category = False
    threshold = 80
    
    similarity_df = pd.DataFrame({'category':[],
                                 'match':[],
                                 'match_rate':[]})
    
    #fuzz.partial_ratio("tomato", "tomatoes")
    
    for i, carbon_category in enumerate(carbon_categories):
        fuzzy_similarities = []
        for category_syn in carbon_categories[carbon_category]:
            fuzzy_similarity = fuzz.ratio(ingredient, category_syn)
            fuzzy_similarities.append(fuzzy_similarity)

        fuzzy_similarities = pd.Series(fuzzy_similarities)
        max_similarity_id = fuzzy_similarities.idxmax()
        max_similarity = fuzzy_similarities.max()
        
        similarity_df.loc[i]=[carbon_category,
                              carbon_categories[carbon_category][max_similarity_id],
                              max_similarity]
        
    max_similarity_rate = similarity_df['match_rate'].max()
    max_similarity_id = similarity_df['match_rate'].idxmax()
    max_similarity_df = similarity_df.loc[max_similarity_id]
    
    if max_similarity_rate > threshold:
        found = True
        match_category = max_similarity_df['category']
    
    return found, match_category


def find_rule_matches(ingredient):
    found = False
    match_category = False
    if ingredient == 'mince':
        match_category = 'beef'
    
    if match_category != False:
        found = True
        
    return found, match_category 


def get_carbon_cat(ingredient, carbon_categories):
    print(f'categorising: {ingredient}')
    found = False
    category_match = ''

    # test for exact matches
    found, category_match = find_exact_match(ingredient, carbon_categories)
    if found:
        log_id = log_match(ingredient, category_match, "exact")
        return vars(MatchedCategory(ingredient, category_match, log_id))
    
    # test for rule matches
    found, category_match = find_rule_matches(ingredient) 
    if found:
        log_id = log_match(ingredient, category_match, "rule")
        return vars(MatchedCategory(ingredient, category_match, log_id))
    
    # then test for fuzzy matches   
    found, category_match = find_fuzzy_match(ingredient, carbon_categories)
    if found:
        log_id = log_match(ingredient, category_match, "fuzzy")
        return vars(MatchedCategory(ingredient, category_match, log_id))

    # # if semantic flag enabled
    if os.getenv("USE_SEMANTIC_SERVICE") == 'True':
        # # test for semantic matches
        x = requests.post(os.getenv("SEMANTIC_SERVICE_URI"), json={"name": ingredient})
        response = json.loads(x.text)
        if response['found'] :
            log_id = log_match(ingredient, response["matched"], "semantic")
            return vars(MatchedCategory(ingredient, response["matched"], log_id))
    

    # # still not found set to misc
    category_match = 'misc'
    log_id = log_match(ingredient, category_match, "misc")

    print(category_match)

    return vars(MatchedCategory(ingredient, category_match, log_id))


def get_carbon_categories(ingredients, carbon_categories):
    ingredient_output = []

    for ingredient in ingredients:
        ingredient_output.append(
            get_carbon_cat(ingredient, carbon_categories)
        )

    return ingredient_output