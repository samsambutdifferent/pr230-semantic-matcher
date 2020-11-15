from flask import Flask, request
from flask_cors import CORS
from carbon_classifier import get_carbon_cat, get_carbon_categories, load_carbon_categories, get_category_syns_dict
import spacy

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "https://pr230-ui-xu26by35cq-ew.a.run.app"}})
# cors = CORS(app, resources={r"*": {"origins": "http://localhost:8080"}})

path = 'data/model_training_data/'
carbon_categories = load_carbon_categories(path)
category_syns_dict = get_category_syns_dict(carbon_categories)


@app.route('/match', methods=['POST'])
def match():
    try:
        req_data = request.get_json()
        print(req_data)
        ingredient = req_data.get('ingredient', '')

        if ingredient != '':
            return get_carbon_cat(ingredient, carbon_categories, category_syns_dict)
        else:
            return "Record not found", 400 

    except Exception as e:
        return f"unable to match ingredient, error {str(e)}"


@app.route('/matchmutiple', methods=['POST'])
def match_mutiple():
    try:
        req_data = request.get_json()

        matched_ingredients = get_carbon_categories(req_data, carbon_categories, category_syns_dict)
        
        return str(matched_ingredients)
    except Exception as e:
        return f"unable to match ingredients list, error {str(e)}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)                