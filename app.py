from flask import Flask, request, jsonify
from flask_cors import CORS
from carbon_classifier import get_carbon_cat, get_carbon_categories, load_carbon_categories, get_category_syns_dict
import spacy
import os
from dotenv import load_dotenv
load_dotenv()
UI_URL = os.getenv("UI_URL")

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": UI_URL}})

path = 'data/model_training_data/'
carbon_categories = load_carbon_categories(path)
category_syns_dict = get_category_syns_dict(carbon_categories)


@app.route('/match', methods=['POST'])
def match():
    """matches a single ingredient with a category
        params:
            type: string
            fomat: "ingredient name"
        return:
            type: dict
            format: {"orignal:" "ingredient name", "matched": "category name"}
    """
    try:
        ingredient = request.get_json()

        if ingredient != '':
            return get_carbon_cat(ingredient, carbon_categories, category_syns_dict)
        else:
            return "Record not found", 400 

    except Exception as e:
        return f"unable to match ingredient, error {str(e)}"


@app.route('/matchmultiple', methods=['POST'])
def match_mutiple():
    """matches mutiple ingredients with appropriate category
        params:
            type: list[string..]
            fomat: ["ingredient name", ..]
        return:
            type: object{list[dict..]}
            format: {"items": [{"orignal:" "ingredient name", "matched": "category name"}]}
    """
    try:
        ingredients = request.get_json()
        return jsonify(items=get_carbon_categories(ingredients, carbon_categories, category_syns_dict))
    except Exception as e:
        return f"unable to match ingredients list, error {str(e)}"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)