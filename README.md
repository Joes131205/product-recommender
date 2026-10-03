# Product Recommender

An product recommendation engine that clusters customers into behavioral segments and filters recommendations by predicted profitability.

---

## 1. Project Overview
* **Backend**: FastAPI REST API serving customer segments and profitable recommendations via SQLite pushdown queries.
* **Frontend**: Streamlit dashboard communicating with the FastAPI service via HTTP.

---

## 2. Modelling Tasks
* **Customer Segmentation (Unsupervised)**: K-Means clustering with `StandardScaler` on RFM features to group customers by purchasing habits.
* **Profitability Filtering (Supervised)**: Classification pipeline to predict and filter out loss-making items among candidate products.

---

## 3. Folder Structure
```text
.
├── backend/
│   ├── app.py                      # FastAPI app
│   └── requirements.txt            # Backend dependencies
├── frontend/
│   ├── frontend.py                 # Streamlit UI
│   └── requirements.txt            # Frontend dependencies
├── model/
│   ├── profit_classification.pkl   # Classification pipeline
│   ├── user_clustering.pkl         # K-Means model
│   └── rfm_scale.pkl               # RFM scaler
├── notebook/
│   ├── index.ipynb                 # Model training file
│   ├── requirements.txt            # Notebook dependencies
├── superstore.sqlite               # Database with customer_segments table
└── README.md

```

---

## 4. Setup & Run Instructions

### Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```

### Backend (Terminal 1)

```powershell
pip install -r backend/requirements.txt
cd backend
python -m uvicorn app:app --reload

```

* **API Docs**: `http://127.0.0.1:8000/docs`

### Frontend (Terminal 2)

```powershell
pip install -r frontend/requirements.txt
cd frontend
..\.venv\Scripts\python.exe -m streamlit run frontend.py

```

* **Dashboard**: `http://localhost:8501`


