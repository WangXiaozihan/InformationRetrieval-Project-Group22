# 🍔 Information Retrieval System - Group 22

## 🚀 Project Overview

This repository contains the source code, data, and documentation for the Information Retrieval System developed by Group 22. The system is designed to index, query, and rank menu items from major fast-food chains (**KFC, McDonald's, and Wendy's**), utilizing **Apache Solr** as the core search engine.

The project encompasses the full IR pipeline: data acquisition (crawling), preprocessing, indexing, search interface implementation, and user evaluation.

---

## 🛠️ Environment & Prerequisites

* **Programming Language:** Python 3.12.9
* **Search Engine:** Apache Solr 9.10.0

---

## 📂 Repository Structure

The project is organized into four main modules:

### 1. Data Acquisition & Preprocessing (`1_Data_Acquisition`)

This directory handles the complete data pipeline from web scraping to Solr-ready files.

| Directory / File                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| :------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`1.1_Crawler_Scripts`**       | Contains web scraping scripts for **KFC, McDonald's, and Wendy's**. <br>⚠️ **Important:** The **KFC** crawler targets the UK website. A **UK-region VPN** is required to run this script successfully.                                                                                                                                                                                                                                                                                |
| **`1.2_Raw_Data`**              | Stores the original, unprocessed data scraped directly from the websites.                                                                                                                                                                                                                                                                                                                                                                                                            |
| **`1.3_Preprocessing_Scripts`** | Scripts for data cleaning and transformation: <br> • **`data_processing_en.py`**: Loads raw data from all brands, performs unified structuring, category mapping, and **imputation** for missing nutritional values. Outputs a unified JSON. <br> • **`data_processing02_en`**: Prepares data for Solr Schema. Creates the **`catch_all_text`** field (merging Name, Description, Category, Ingredients for full-text search) and calculates the **`popularity_score`** for ranking. |
| **`1.4_Processed_Data`**        | Contains the final, cleaned JSON files ready for direct import into Solr.                                                                                                                                                                                                                                                                                                                                                                                                            |
| **`1.5_Synonyms_generation`**   | Uses data from `1.4` to generate a **Synonyms Table**. This table is imported into Solr to enhance query matching (e.g., handling abbreviations or alternate terms).                                                                                                                                                                                                                                                                                                                 |

### 2. Solr Configuration (`2_Solr_Configuration`)

This folder contains the essential configuration files for setting up the Solr Core.

* **Configuration Files:** Includes `solrconfig.xml` and `managed-schema` (or `schema.xml`).
* **Schema Details:** Defines field types and the custom fields generated in step 1.3 (`catch_all_text`, `popularity_score`).
* **Data Storage:** May contain core data structures required for Solr initialization.

### 3. Search Interface (`3_Search_Interface`)

This directory contains the implementation of the user-facing search application, built using the **Nuxt.js** framework.

* **Frontend:** Developed with **Nuxt.js** (Vue.js based), utilizing HTML, CSS, and JavaScript for a responsive and interactive user experience.
* **Key Functionality:**
    * **Advanced Filtering (Faceted Search):** Users can filter search results based on:
        * **Fast Food Chain** (Company)
        * **Food Category**
        * **Nutritional Content:** Filters for **Salt**, **Fat**, and **Calories**.
    * **User Relevance Feedback:** Implemented a **Relevance Feedback** mechanism to refine query results based on user interactions, improving retrieval accuracy over time.
    * **Visualization:** Displays search results with detailed metadata (price, nutrition info).

### 4. User Evaluation (`4_User_Evaluation`)

This section documents the experimental design and results used to assess the system's performance and usability.

* **`4.1_Test_Questionnaire`**: Contains the **User Tasks** scripts and the **System Usability Scale (SUS)** original questionnaires used in the study.
* **`4.2_User_Study_Data`**: Stores the raw data collected from user surveys and the statistical analysis results.
* **`4.3_Final_Report_Material`**: Contains charts, graphs, and summary data generated for the final project report.

---

## 🚦 Quick Start Guide

1.  **Clone the Repository:**
    ```bash
    git clone [Your Repository Link]
    ```
2.  **Data Setup:**
    * If re-crawling is needed, ensure VPN is set for KFC scripts in `1.1`.
    * Run scripts in `1.3` to regenerate processed data if modifying logic.
    * Generate synonyms using `1.5`.
3.  **Solr Initialization:**
    * Start Solr 9.10.0.
    * Create a core and copy configurations from `2_Solr_Configuration`.
    * Import data from `1.4_Processed_Data`.
4.  **Launch Interface:**
    * Navigate to `3_Search_Interface` and launch the application

---

## 👥 Group Members

* Xiaozihan Wang
* Yujia Wang