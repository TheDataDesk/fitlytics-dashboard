# 🏋️‍♀️ Fitlytics Dashboard

**Fitlytics** is an interactive dashboard built using Streamlit to help explore business insights for a fictional athletic e-commerce brand. Whether you're looking to understand customer retention patterns, revenue performance, or product category trends — this dashboard brings it all together in a visually intuitive and insightful way.

---

## What You will Discover

Dive deep into real-world e-commerce questions:

- Which customer cohorts are more loyal?
- When and where does customer churn occur?
- What categories and products drive the most revenue?
- How do discount strategies influence retention?
- What does our business health look like month over month?

---

## Tech Stack

- **Python 3.13.3**
- **Streamlit** – for the frontend dashboard
- **Pandas** – for data manipulation
- **Plotly** – for interactive visualizations
- **Parquet** – for fast, efficient data storage

---

## Project Structure

fitlytics-dashboard/
├── app.py # Main Streamlit dashboard
├── analysis.py # Business logic and metric calculations
├── transform.py # Data cleaning and preprocessing
├── visualization.py # Plotly chart rendering functions
├── loader.py # Optional: utilities for loading data
├── requirements.txt # Project dependencies
├── README.md # This file
└── data/
├── orders.parquet # Order-level transaction data
└── products.parquet # Product-level metadata

---

## Getting Started

Follow these steps to run the dashboard locally:

### 1. Clone the Repository

```bash
git clone https://github.com/TheDataDesk/fitlytics-dashboard.git
cd fitlytics-dashboard
```
---

### 2. Set Up a Virtual Environment


python3.13 -m venv venv
source venv/bin/activate     # If you are on Windows: venv\Scripts\activate

--- 
### 3.  Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

If requirements.txt is missing, install manually:

pip install streamlit pandas plotly pyarrow

**Make sure your system has **Python 3.13.3 or later** installed.**


---

### 5. Run the Dashboard

streamlit run app.py

---
### 6. Dataset Period
The dashboard analyzes transactional data from:
 December 3, 2019 to March 8, 2021

 ---

# 7. About This Project

This dashboard was built as part of a data challenge by Hey Holy, a brand in the pet wellness space. The task was simple: take a raw e-commerce dataset and bring it to life with real, actionable insights.

I focused on things that truly matter to a growing brand — customer retention, product trends, revenue patterns, and the impact of discounts. The result is a clean, interactive dashboard where anyone (not just data folks) can explore what’s really driving the business.

--- 

Curious to explore it yourself?

[Click here for Live dashboard](https://fitlytics-dashboard.streamlit.app/)