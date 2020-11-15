from flask import Flask, request
from flask_cors import CORS
from carbon_classifier import get_carbon_categories, load_carbon_categories, get_category_syns_dict
from co2_index_table import return_all_available_ingredients, calculate_food_item_co2_index
import spacy

app = Flask(__name__)
# cors = CORS(app, resources={r"*": {"origins": "https://landing-page-xu26by35cq-ew.a.run.app"}})
cors = CORS(app, resources={r"*": {"origins": "https://pr230-ui-xu26by35cq-ew.a.run.app"}})
# cors = CORS(app, resources={r"*": {"origins": "http://localhost:8080"}})

path = 'data/model_training_data/'
carbon_categories = load_carbon_categories(path)
category_syns_dict = get_category_syns_dict(carbon_categories)
nlp = spacy.load("en_core_web_lg")

@app.route('/', methods=['POST'])
def calculate_carbon_index_of_food_item():
    try:
        req_data = request.get_json()

        matched_ingredients = get_carbon_categories(req_data, carbon_categories, category_syns_dict, nlp)

        ingredients = matched_ingredients['carbon_categories']
        print(ingredients)
        
        return str(calculate_food_item_co2_index(ingredients))
    except Exception as e:
        return f"unable to calculate food item index, error {str(e)}"


@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    try:
        ingredients = return_all_available_ingredients()
        return { i : ingredients[i] for i in range(0, len(ingredients) ) }
    except Exception as e:
        return f"unable to get ingredients list, error: {str(e)}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)                