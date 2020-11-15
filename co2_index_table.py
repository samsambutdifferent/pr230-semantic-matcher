import pandas as pd
import os

CSV_PATH=os.path.join('.','data/co2_index.csv')
COLS_TO_USE=['name', 'co2_index_per_g']
df = pd.read_csv(CSV_PATH,
                 usecols=COLS_TO_USE)


def calculate_food_item_co2_index(ingredientList):
    '''
        Sum together all co2 values to get total
    '''
    totalSum=0
    for key,value in ingredientList.items():
        totalSum += calculate_ingredient_co2_index(value, key)
    return totalSum
        

def calculate_ingredient_co2_index(grams, name):
    '''
        Get c02 per gram value from co2 index table
    '''
    isName = df['name'] == name
    filtered = df[isName]
    co2Val = filtered['co2_index_per_g'].iloc[0]
    return co2Val * grams
    
def return_all_available_ingredients():
    '''
        return list of all currently available food items
    '''
    return pd.unique(df['name'])
    