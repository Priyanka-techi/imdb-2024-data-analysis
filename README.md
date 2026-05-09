# 🎬 IMDb 2024 Data Scraping and Visualizations

An end-to-end data analytics project that scrapes IMDb’s 2024 movie dataset, processes and stores it in a structured database, and presents interactive insights through a Streamlit dashboard.

---

## 📌 Project Overview

| Item              | Detail                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------- |
| **Domain**        | Entertainment / Data Analytics                                                               |
| **Skills Gained** | Selenium · Python · Pandas · SQL · Data Cleaning · Data Analysis · Visualization · Streamlit |
| **Database**      | SQLite (can be switched to PostgreSQL/MySQL)                                                 |
| **Data Source**   | IMDb 2024 Movies                                                                             |

---

## ❓ Problem Statement

This project focuses on extracting and analyzing movie data from IMDb for the year 2024. The system scrapes movie details such as name, genre, ratings, votes, and duration using Selenium, processes the data, and stores it in an SQL database.

An interactive Streamlit dashboard is built to visualize insights and allow users to explore the dataset using filters.

---

## 🎯 Business Use Cases

* 🔝 Top-Rated Movies
* 🎭 Genre Distribution Analysis
* ⏱ Duration Insights by Genre
* 👍 Voting Trends Analysis
* 📊 Popular Genres Identification
* ⭐ Rating Distribution
* 🥇 Genre-wise Top Movies
* 📉 Correlation between Ratings & Votes
* 🎬 Duration Extremes (Shortest / Longest)
* 🎛 Interactive Filtering for custom insights

---

## 🛠️ Approach

### 1️⃣ Data Scraping & Storage

* Scraped IMDb 2024 movies using Selenium
* Extracted:

  * Movie Name
  * Genre
  * Ratings
  * Voting Counts
  * Duration
* Stored data:

  * Genre-wise CSV files
  * Master dataset
* Merged and saved into SQL database

---

### 2️⃣ Data Cleaning & Processing

* Removed duplicates and missing values
* Converted:

  * Duration → minutes
  * Votes → numeric values (K, M handling)
* Standardized genre labels
* Prepared final clean dataset

---

### 3️⃣ Data Analysis & Visualization

Interactive dashboard built using Streamlit:

#### 📊 Visualizations

1. Top 10 Movies by Rating
2. Top 10 Movies by Votes
3. Genre Distribution
4. Average Duration by Genre
5. Voting Trends by Genre
6. Rating Distribution
7. Genre-Based Rating Leaders
8. Most Popular Genres by Voting
9. Duration Extremes
10. Ratings by Genre (Heatmap)
11. Ratings vs Votes Correlation

---

### 🎛 Interactive Filtering

Users can filter data by:

* ⭐ Ratings
* 👍 Voting Counts
* ⏱ Duration
* 🎭 Genre

Filters can be combined for customized insights.

---

## 📁 Project Structure

```
imdb-2024-project/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│
├── scripts/
│   ├── scraper.py
│   ├── clean_data.py
│   └── db_upload.py
│
├── app/
│   └── app.py
│
├── database/
│   └── movies.db
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/imdb-2024-project.git
cd imdb-2024-project
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup ChromeDriver

Download matching version and add to PATH.

---

## 🚀 Execution Steps

### Step 1 — Scrape Data

```bash
python scripts/scraper.py
```

### Step 2 — Clean Data

```bash
python scripts/clean_data.py
```

### Step 3 — Upload to Database

```bash
python scripts/db_upload.py
```

### Step 4 — Run Dashboard

```bash
streamlit run app/app.py
```

---

## 🗂 Dataset Columns

| Column     | Description        |
| ---------- | ------------------ |
| Movie Name | Movie title        |
| Genre      | Genre/category     |
| Ratings    | IMDb rating        |
| Votes      | Number of votes    |
| Duration   | Runtime in minutes |

---

## 🔧 Tech Stack

* **Language:** Python
* **Scraping:** Selenium
* **Data Processing:** Pandas, NumPy
* **Database:** SQLite (SQLAlchemy)
* **Visualization:** Matplotlib, Seaborn
* **Dashboard:** Streamlit

---

## 📌 Project Deliverables

* ✅ SQL Database
* ✅ Python Scripts (Scraping + Cleaning + DB)
* ✅ Streamlit Dashboard
* ✅ CSV Dataset (Genre-wise + Master)

---

## ⚠️ Troubleshooting

| Issue              | Solution                      |
| ------------------ | ----------------------------- |
| ChromeDriver error | Match Chrome version          |
| Data not found     | Run scripts in order          |
| IMDb blocked       | Retry after some time         |
| App crash          | Ensure dependencies installed |

---

## 📊 Evaluation Criteria Covered

* ✔ Maintainable code structure
* ✔ Cross-platform compatibility
* ✔ Modular design
* ✔ Proper documentation
* ✔ Interactive dashboard

---

## 🎥 Demo (Add Here)

👉 Add your demo video / LinkedIn post link here

---
