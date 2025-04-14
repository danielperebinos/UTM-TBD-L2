# 🏨 Big Data Technologies – Hotel Reviews Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-Used-green)](https://docs.docker.com/compose/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-brightgreen)](https://www.mongodb.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-orange)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)

This project was developed as part of the **Big Data Technologies** course and demonstrates a complete pipeline for
processing, storing, and analyzing hotel reviews at scale using **MongoDB**, **Streamlit**, and **Docker**.

---

## 🧩 Project Structure

```
📦 root/
 ├── compose.yaml               # Docker config for MongoDB
 ├── converter.py              # Transforms raw CSV to MongoDB-ready JSON
 ├── main.py                   # Streamlit dashboard frontend
 ├── analysis.ipynb           # Exploratory data analysis (EDA)
 └── datasets/                 # Transformed JSON data for import
```

---

## 🛠 Technologies Used

- **MongoDB**: NoSQL document store used for hotel and review data.
- **Pandas**: For data manipulation and transformation.
- **Streamlit**: For building the interactive dashboard.
- **Docker Compose**: For easy deployment of MongoDB in a containerized environment.
- **Matplotlib**: For visualizations embedded in Streamlit.
- **Hashlib / ObjectId**: For deterministic and unique review and hotel identifiers.

---

## ⚙️ Functionality Overview

### 🧪 `converter.py`

- Loads raw hotel review CSVs.
- Deduplicates hotels and generates consistent MongoDB-compatible `ObjectId`s.
- Splits data into:
    - `hotels.json`: Clean hotel info
    - `reviews.json`: Normalized and enriched reviews with embedded reviewer profiles
- Saves them into the `datasets/` folder for import into MongoDB.

---

### 🧾 `compose.yaml`

- Spins up a MongoDB instance at port `27020`
- Auto-initializes with root credentials
- Persistent volume: `tbd_mongo_data` for data durability.

---

### 📊 `main.py` – Streamlit Dashboard

**Includes:**

1. **✍️ Submit Review**
    - Allows new reviews to be inserted via the UI into the MongoDB collection.

2. **📊 Hotel Statistics**
    - Filters by hotel, nationality, and score range.
    - Aggregates and ranks hotels by average score and number of reviews.
    - Displays results with pagination and dynamic bar charts.

3. **🔍 Explore Reviews**
    - Keyword-based search with multiple filters.
    - Display review highlights, reviewer info, and allows deletion of entries.

All operations are performed live against the MongoDB backend using `pymongo`.

---

### 📈 `analysis.ipynb`

- Performs initial data inspection and insights.
- Includes basic statistics, distributions, and exploratory plots.

---

## 🚀 Running the Project

### 1. Launch MongoDB

```bash
docker compose up -d
```

### 2. Preprocess Data

```bash
python converter.py
```

### 3. Import Data into MongoDB (optional)

```bash
mongoimport --uri mongodb://root:root@localhost:27020/hotels --collection hotels --file datasets/hotels.json --jsonArray
mongoimport --uri mongodb://root:root@localhost:27020/hotels --collection reviews --file datasets/reviews.json --jsonArray
```

### 4. Run the Streamlit Dashboard

```bash
streamlit run main.py
```

---

## Schema

```mermaid
erDiagram
    HOTEL ||--o{ REVIEW: has
    REVIEWER ||--o{ REVIEW: writes

    HOTEL {
        string _id
        string name
        string address
        float average_score
        int total_number_of_reviews
        float lat
        float lng
    }

    REVIEW {
        string _id
        string hotel_id
        string user_id
        string review_date
        string positive_review
        string negative_review
        int review_total_positive_word_counts
        int review_total_negative_word_counts
        float reviewer_score
        string[] tags
        string days_since_review
    }

    REVIEWER {
        string nationality
        int total_number_of_reviews_by_reviewer
    }
```

---

## 📄 License

This project is licensed under the MIT License.