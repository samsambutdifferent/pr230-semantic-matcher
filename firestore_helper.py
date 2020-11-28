
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
firebase_collection = 'carbon_matches'

def load_carbon_matches():
    """loads matches from firestore db
        return:
            type: dict
            format: {'name': ['synonnym one', 'synonym two',...], ..}
    """
    carbon_matches = {}
    collection = db.collection(firebase_collection).get()

    # for all documents in collection carbon_matches
    for document in collection:
        doc_dict = document.to_dict()

        carbon_matches[doc_dict['name']] = doc_dict['matches']
    
    return carbon_matches


