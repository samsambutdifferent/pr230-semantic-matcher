
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from datetime import datetime


cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
firebase_collection = 'categories'

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
        u'log_id': log_id,
        u'matched': matched,
        u'original': original,
        u'reviewed': False
    }

    print(f"reporting: {data}")

    try:
        db.collection(u'reported').document(str(date_time)).set(data)
    except Exception as e:
        print(f"failed reporting: {e}")