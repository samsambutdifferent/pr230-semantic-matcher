import os
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
firebase_collection = "categories"



def load_carbon_matches():
    """loads matches from firestore db
    return:
        type: dict
        format: {'name': ['synonnym one', 'synonym two',...], ..}
    """
    carbon_matches = {}
    alternatives = {}
    collection = db.collection(firebase_collection).get()

    # for all documents in collection carbon_matches
    for document in collection:
        doc_dict = document.to_dict()

        carbon_matches[doc_dict["name"]] = doc_dict["matches"]

        alt = doc_dict.get("alternatives", [])

        alternatives[doc_dict["name"]] = alt

    return alternatives,carbon_matches


def write_to_reported(log_id, matched, original):
    """writes value to reported firebase table
    params:
        log_id
            type: string
        matched
            type: string
        original
            type: string
    """
    date_time = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
    data = {
        "log_id": log_id,
        "matched": matched,
        "original": original,
        "reviewed": False,
    }

    print(f"reporting: {data}")

    try:
        db.collection("reported").document(str(date_time)).set(data)
    except Exception as e:
        print(f"failed reporting: {e}")
