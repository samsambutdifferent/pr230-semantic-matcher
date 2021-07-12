import os
import sys

import spacy
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from carbon_classifier import get_carbon_cat, get_carbon_categories
from firestore_helper import load_carbon_matches

load_dotenv()
uris = os.getenv("URIS").split(",")

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": uris}})

carbon_categories = load_carbon_matches()


@app.route("/wakeup", methods=["GET"])
def wake_up():
    """starts the api
    params:
    return:
        type: string
    """
    try:
        return "started api", 200
    except Exception as e:
        sys.stdout.flush()
        return f"unable to start api {str(e)}", 400


@app.route("/match", methods=["POST"])
def match():
    """matches a single ingredient with a category
    params:
        type: dict
        fomat: {name: "ingredient name"}
    return:
        type: dict
        format: {"original:" "ingredient name", "matched": "category name"}
    """
    try:
        js = request.get_json()
        ingredient = js.get("name", "")

        if ingredient != "":
            sys.stdout.flush()
            return get_carbon_cat(ingredient, carbon_categories)
        else:
            sys.stdout.flush()
            return "Record not found", 400

    except Exception as e:
        sys.stdout.flush()
        return f"unable to match ingredient, error {str(e)}"


@app.route("/matchmultiple", methods=["POST"])
def match_mutiple():
    """matches mutiple ingredients with appropriate category
    params:
        type: list[string..]
        fomat: ["ingredient name", ..]
    return:
        type: object{list[dict..]}
        format: {"items": [{"original:" "ingredient name", "matched": "category name"}]}
    """
    try:
        ingredients = request.get_json()
        sys.stdout.flush()
        return jsonify(items=get_carbon_categories(ingredients, carbon_categories))
    except Exception as e:
        sys.stdout.flush()
        return f"unable to match ingredients list, error {str(e)}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
