import pandas as pd
import numpy as np
import os
import spacy
from fuzzywuzzy import fuzz
from firestore_helper import load_carbon_matches
from helper import log_match

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


def get_category_syns_dict(carbon_categories):
    
    nlp = spacy.load("en_core_web_lg")  
    
    category_syns_dict = {}
    for i, carbon_category in enumerate(carbon_categories):
        category_syns_dict[carbon_category] = {}
        for category_syn in carbon_categories[carbon_category]:
            category_syns_dict[carbon_category][category_syn] = nlp(category_syn)
            
    return category_syns_dict


def find_semantic_match(ingredient, carbon_categories, category_syns_dict):
    
    found = False 
    match_category = False
    threshold = 80
    
    similarity_df = pd.DataFrame({'category':[],
                                 'match':[],
                                 'match_rate':[]})
    
    token = nlp(ingredient)
    
    if (token.has_vector) & (token.vector.sum()!=0):
    
        for i, carbon_category in enumerate(carbon_categories):
            semantic_similarities = []
            for category_syn in carbon_categories[carbon_category]:
                category_syn_token = category_syns_dict[carbon_category][category_syn]
                if (category_syn_token.has_vector) & (category_syn_token.vector.sum()!=0):
                    semantic_similarity = token.similarity(category_syn_token) * 100
                    semantic_similarities.append(semantic_similarity)

            semantic_similarities = pd.Series(semantic_similarities)
            max_similarity_id = semantic_similarities.idxmax()
            max_similarity = semantic_similarities.max()

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


def get_carbon_cat(ingredient, carbon_categories, category_syns_dict):
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
    
    # # test for semantic matches
    found, category_match = find_semantic_match(ingredient, carbon_categories, category_syns_dict)
    if found:
        log_id = log_match(ingredient, category_match, "semantic")
        return vars(MatchedCategory(ingredient, category_match, log_id))

    # # still not found set to misc
    log_id = log_match(ingredient, category_match, "Not Found")
    category_match = 'misc'

    return vars(MatchedCategory(ingredient, category_match, log_id))


def get_carbon_categories(ingredients, carbon_categories, category_syns_dict):
    ingredient_output = []

    for ingredient in ingredients:
        ingredient_output.append(
            get_carbon_cat(ingredient, carbon_categories, category_syns_dict)
        )

    return ingredient_output