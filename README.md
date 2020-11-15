# pr230-semantic-matcher

## setup

python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt

### Spacy model

this will take ages... 

```bash
    python -m spacy download en_core_web_lg
```

### run

python app.py


## deployment

### manual

gcloud builds submit --tag gcr.io/project2030/semantic-matcher

gcloud run deploy --image gcr.io/project2030/semantic-matcher --platform managed --region europe-west1 --allow-unauthenticated