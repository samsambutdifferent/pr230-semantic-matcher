import pandas as pd
import numpy as np
import os
import spacy
from fuzzywuzzy import fuzz

def load_carbon_categories(path):

    carbon_category_files = os.listdir(path)

    carbon_categories = {}
    for carbon_category_file in carbon_category_files:
        if '.ipynb' not in carbon_category_file:
            carbon_category_syns = pd.read_csv(path+carbon_category_file)
            carbon_category_syns = carbon_category_syns.T[0].values
            carbon_categories[carbon_category_file.split('_types.csv')[0]] = carbon_category_syns
            
    return carbon_categories


def find_exact_match(ingredient, carbon_categories):
    found = False
    match_category = False

    for carbon_category in carbon_categories: 
        if ingredient in carbon_categories[carbon_category]:
            found = True
            match_category = carbon_category
            print(f'exact match: {match_category}')

    
    return found, match_category


def get_category_syns_dict(carbon_categories):
    
    nlp = spacy.load("en_core_web_lg")  
    
    category_syns_dict = {}
    for i, carbon_category in enumerate(carbon_categories):
        category_syns_dict[carbon_category] = {}
        for category_syn in carbon_categories[carbon_category]:
            category_syns_dict[carbon_category][category_syn] = nlp(category_syn)
            
    return category_syns_dict


def find_semantic_match(ingredient, carbon_categories, category_syns_dict, nlp):
    
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
                #print(category_syn)
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

        #print(list(max_similarity_df.values))

        if max_similarity_rate > threshold:
            found = True
            match_category = max_similarity_df['category']
            print(f'semantic match: {match_category}')
   
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
    
    #print(list(max_similarity_df.values))
    
    if max_similarity_rate > threshold:
        found = True
        match_category = max_similarity_df['category']
        print(f'fuzzy match: {match_category}')

    
    return found, match_category


def find_rule_matches(ingredient):
    found = False
    match_category = False
    if ingredient == 'mince':
        match_category = 'beef'
    
    if match_category != False:
        found = True
        print(f'rule match: {match_category}')
        
    return found, match_category 


def get_carbon_categories(ingredient_input, carbon_categories, category_syns_dict, nlp):

    ingredient_output = {'carbon_categories':{}}

    for ingredient in ingredient_input['ingredients']:
        print(f'categorising: {ingredient}')
        found = False

        # first test for exact matches
        found, category_match = find_exact_match(ingredient, carbon_categories)
        # then test for rule matches
        if not found:
            found, category_match = find_rule_matches(ingredient)        
        # then test for fuzzy matches
        if not found:
            found, category_match = find_fuzzy_match(ingredient, carbon_categories)
        # then test for semantic matches
        if not found:
            found, category_match = find_semantic_match(ingredient, carbon_categories, category_syns_dict, nlp)
        # then run the update carbon db method. this should be toggled on and off   
        if not found:
            print(f'{ingredient} not found - should log this')
            category_match = 'misc'
        print(category_match)


        ingredient_output['carbon_categories'][category_match] = ingredient_input['ingredients'][ingredient]
    
    return ingredient_output