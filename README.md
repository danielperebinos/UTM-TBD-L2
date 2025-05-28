# 🏦 Bank Customer & Transactions Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-Used-green)](https://docs.docker.com/compose/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-brightgreen)](https://www.mongodb.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-orange)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Descriere Proiect

Acest proiect este o aplicație demo pentru gestionarea și vizualizarea datelor bancare privind clienții și tranzacțiile
acestora.  
Folosește un backend MongoDB pentru stocarea datelor, o interfață Streamlit pentru interacțiunea cu utilizatorul și este
ușor de deploy-at prin Docker Compose.

---

## 🧩 Structura Proiectului

```plaintext
📦 root/
 ├── compose.yaml             # Configurare Docker Compose pentru MongoDB
 ├── converter.py            # Script de transformare CSV în JSON pregătit pentru MongoDB
 ├── main.py                 # Dashboard Streamlit pentru gestionarea datelor
 ├── analysis.ipynb          # Notebook pentru explorarea inițială a datelor
 ├── README.md               # Documentația proiectului
 └── datasets/               # Date JSON preprocesate pentru import în MongoDB
````

---

## 🛠 Tehnologii utilizate

* **Python 3.10+** – Limbaj de programare principal
* **MongoDB** – Bază de date NoSQL pentru stocarea clienților și tranzacțiilor
* **Streamlit** – Interfață web interactivă pentru vizualizare și administrare
* **Docker Compose** – Pentru orchestrarea containerului MongoDB
* **Pandas** – Manipularea și procesarea datelor
* **Hashlib** – Generarea identificatorilor unici deterministici
* **Matplotlib** – Vizualizări (în notebook și în dashboard)

---

## ⚙️ Funcționalități principale

### `converter.py`

* Încarcă datele brute din CSV
* Creează identificatori unici tip ObjectId pentru clienți și tranzacții
* Generează fișiere JSON gata de importat în MongoDB:

    * `customers.json`
    * `transactions.json`

---

### `compose.yaml`

* Configurează și pornește un container MongoDB pe portul `27020`
* Setează credențiale root
* Volum persistent pentru date

---

### `main.py` – Dashboard Streamlit

Dashboard-ul este împărțit în trei taburi principale:

1. **✍️ Adăugare Date**

    * Formulare pentru adăugarea de clienți noi
    * Formulare pentru adăugarea tranzacțiilor aferente clienților existenți

2. **📊 Vizualizare Date**

    * Vizualizare paginată și filtrabilă pentru clienți și tranzacții
    * Filtre după gen, locație, sumă tranzacție, tip tranzacție etc.

3. **🔍 Căutare și Actualizare**

    * Căutare clienți și tranzacții după ID
    * Actualizare sold cont sau suma tranzacției
    * Ștergere clienți și tranzacții

---

## 📈 Analiză și explorare date (`analysis.ipynb`)

* Explorare inițială a datasetului
* Statistici descriptive și grafice pentru datele clienților și tranzacțiilor

---

## 🚀 Cum rulezi proiectul

### 1. Pornește MongoDB cu Docker Compose

```bash
docker compose up -d
```

### 2. Transformă datele CSV în JSON pentru import

```bash
python converter.py
```

### 3. (Opțional) Importă datele în MongoDB

```bash
mongoimport --uri mongodb://root:root@localhost:27020/bank --collection customers --file datasets/customers.json --jsonArray
mongoimport --uri mongodb://root:root@localhost:27020/bank --collection transactions --file datasets/transactions.json --jsonArray
```

### 4. Rulează dashboard-ul Streamlit

```bash
streamlit run main.py
```

---

## 🗂 Schema colecțiilor MongoDB

```mermaid
erDiagram
    CUSTOMER ||--o{ TRANSACTION: owns

    CUSTOMER {
        string _id
        string customer_id
        string gender
        string location
        float account_balance
    }

    TRANSACTION {
        string _id
        string customer_id
        string transaction_id
        string transaction_date
        float transaction_amount
        string transaction_time
    }
```

---

## 📄 Licență

Acest proiect este licențiat sub licența [MIT](https://opensource.org/licenses/MIT).

---

## 📸 Vizualizări

![Schema colecții](schema.png)
![Arbore decizie](decision_tree.png)
![Exemplu grafic tranzacții](newplot.png)

---

*Proiect dezvoltat ca parte din cursul Big Data Technologies.*
