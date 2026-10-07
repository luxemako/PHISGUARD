# PhishGuard

PhishGuard checks URLs, messages, and emails for phishing risk. It uses machine-learning models, a FastAPI backend, and a React frontend.

The result is only a risk estimate. Do not treat it as proof that a link is safe.

## Requirements

- Python 3.11
- Node.js and npm
- Git Bash on Windows

Run the commands below from the project root.

## 1. Set up the backend

```bash
py -3.11 -m venv backend/venv
source backend/venv/Scripts/activate
python -m pip install -r backend/requirements.txt
```

If the environment already exists, only activate it:

```bash
source backend/venv/Scripts/activate
```

## 2. Set up the frontend

```bash
cd frontend
npm install
cd ..
```

## 3. Add the datasets

Place these files in `datasets/raw/`:

```text
450k URL.csv
phishing_email.csv
```

Dataset sources:

- [URL phishing dataset](https://www.kaggle.com/datasets/xntrng15/url-phishing-dataset)
- [Phishing email dataset](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)

## 4. Prepare the datasets

```bash
python backend/training/prepare_url_dataset.py
python backend/training/prepare_text_dataset.py
```

## 5. Train the models

```bash
python backend/training/train_url_modal.py
python backend/training/train_text_model.py
```

You only need to repeat steps 4 and 5 after changing a dataset or model feature.

## 6. Run the backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

API documentation: <http://127.0.0.1:8000/docs>

Keep this terminal running.

## 7. Run the frontend

Open a second terminal from the project root:

```bash
cd frontend
npm run dev
```

Application: <http://localhost:5173>

## 8. Run checks

Backend tests:

```bash
cd backend
python -m unittest discover -s tests -v
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Common errors

### `No module named pandas`

```bash
source backend/venv/Scripts/activate
python -m pip install -r backend/requirements.txt
```

### The model cannot be loaded

Run the dataset preparation and model training commands from steps 4 and 5.

### The frontend cannot reach the backend

Confirm that the backend is running on port `8000` and the frontend is running on port `5173`.

## Current limitations

- PhishGuard does not open or inspect website content.
- It does not check domain age, DNS reputation, or redirects.
- Prediction quality depends on the training datasets.
