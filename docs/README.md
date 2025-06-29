# Data Engineering Assessment

Welcome! This exercise is designed to evaluate your core skills in **data engineering**:

- **SQL databases**: Data modeling, normalization, and scripting
- **Python and ETL**: Data cleaning, transformation, and loading workflows

---

## 📚 How This Document Works

Each section is structured with:

- **Problem:** Background and context for the task
- **Task:** What you are required to do (including any bonus “extra” tasks)
- **Solution:** Where you must document your approach, decisions, and provide instructions for reviewers

> **Tech Stack:**  
> Please use only Python (for ETL/data processing) and SQL/MySQL (for database).  
> Only use extra libraries if they do not replace core logic, and clearly explain your choices in your solution.

---

## 0. Setup

1. **Fork and clone this repository:**
    ```bash
    git clone https://github.com/<your-username>/homellc_data_engineer_assessment_skeleton.git
    ```
2. **Start the MySQL database in Docker:**
    ```bash
    docker-compose -f docker-compose.initial.yml up --build -d
    ```
    - Database is available on `localhost:3306`
    - Credentials/configuration are in the Docker Compose file
    - **Do not change** database name or credentials

3. For MySQL Docker image reference:  
   [MySQL Docker Hub](https://hub.docker.com/_/mysql)

---

### Problem

You are provided with property-related data in a CSV file.
- Each row relates to a property.
- There are multiple Columns related to this property.
- The database is not normalized and lacks relational structure.


### Task

- **Normalize the data:**
  - Develop a Python ETL script to read, clean, transform, and load   data into your normalized MySQL tables.
  - Refer the field config document for the relation of business logic
  - Use primary keys and foreign keys to properly capture relationships

- **Deliverable:**
  - Write necessary python and sql scripts
  - Place the scripts inside the `sql/` directory)
  - The scripts should take the initial csv to your final, normalized schema when executed
  - Clearly document how to run your script, dependencies, and how it integrates with your database.

**Tech Stack:**  
- Python (include a `requirements.txt`)
Use **MySQL** and SQL for all database work  
- You may use any CLI or GUI for development, but the final changes must be submitted as python/ SQL scripts 
- **Do not** use ORM migrations—write all SQL by hand

# Solution

## Database design & Normalization

### What is normalization?

Database normalization is the process of structuring tables to reduce redundancy and ensure data integrity.

1. **First Normal Form (1NF):** Every column holds atomic values; each row is unique.
2. **Second Normal Form (2NF):** Builds on 1NF by removing partial dependencies—every non-key column depends on the entire primary key.
3. **Third Normal Form (3NF):** Removes transitive dependencies—non-key columns depend only on the primary key, not on other non-key columns.

### Schema design and tables

We split the data into 7 tables, each focused on a single business domain, and linked via surrogate keys to eliminate redundancy and enforce referential integrity:

1. **Address\_info**
   
   **Columns:** `Address_ID (PK)`, `Address`, `Street_Address`, `City`, `State`, `Zip`
    
   **Why:** Centralizes all address details so that every property record points to a single address, avoiding repeated city/state text across rows.

2. **Property**
   
   **Columns:**
   `Property_ID (PK)`, `Property_Title`, `Market`, `Flood`, `Property_Type`,
   `Highway`, `Train`, `Tax_Rate`, `SQFT_Basement`, `HTW`, `Pool`,
   `Commercial`, `Water`, `Sewage`, `Year_Built`, `SQFT_MU`, `SQFT_Total`,
   `Parking`, `Bed`, `Bath`, `BasementYesNo`, `Layout`, `Rent_Restricted`,
   `Neighborhood_Rating`, `Latitude`, `Longitude`, `Subdivision`,
   `School_Average`, `Address_ID (FK)`
    
   **Why:** Holds the core, static attributes of each property. The `Address_ID` FK ensures each property is tied to exactly one address record.

3. **Leads**
   
   **Columns:** `Lead_ID (PK)`, `Property_ID (FK)`, `Reviewed_Status`, `Most_Recent_Status`, `Source`, `Occupancy`, `Net_Yield`, `IRR`, `Selling_Reason`, `Seller_Retained_Broker`, `Final_Reviewer`
    
   **Why:** Captures the all Lead metrics for each property, keeping this volatile data out of the main property table.

4. **Valuation**
   
   **Columns:** `Valuation_ID (PK)`, `Property_ID (FK)`, `Previous_Rent`, `List_Price`, `Zestimate`, `ARV`, `Expected_Rent`, `Rent_Zestimate`, `Low_FMR`,             `High_FMR`, `Redfin_Value`
   
   **Why:** Captures all financial estimates so that complex valuation metrics don’t clutter other tables.

6. **Rehab**
    
   **Columns:** `Rehab_ID (PK)`, `Property_ID (FK)`, `Underwriting_Rehab`, `Rehab_Calculation`, `Paint`, `Flooring_Flag`, `Foundation_Flag`, `Roof_Flag`, `HVAC_Flag`, `Kitchen_Flag`, `Bathroom_Flag`, `Appliances_Flag`, `Windows_Flag`, `Landscaping_Flag`, `Trashout_Flag`
    
   **Why:** Groups all renovation-related fields together, preventing sparsity and simplifying maintenance of rehab data.

7. **HOA**
    
   **Columns:** `HOA_ID (PK)`, `Property_ID (FK)`, `HOA`, `HOA_Flag`
     
   **Why:** Separates homeowners-association details, as not every property has HOA fees.

8. **Taxes**
    
   **Columns:** `Tax_ID (PK)`, `Property_ID (FK)`, `Taxes`
     
   **Why:** Stores tax related data independently, ready for tax-specific queries.

All tables meet 1NF (atomic fields), 2NF (no partial key dependencies), and 3NF (no transitive dependencies).

### How to run and test the SQL scripts

**Start the fully-initialized MySQL container**

   ```bash
   docker-compose -f docker-compose.final.yml up --build -d
   ```

   * This runs `00_init_db_dump.sql` first (in my case this file act as just placeholder for docker), then `99_final_db_dump.sql` (creates full schema).


After this setup is verified, you can run your Python ETL script to load data into each table.

 
## Python ETL logic

### Overview

Python ETL script follows a clear Extract → Transform → Load pattern:

1. **Extract:** Read raw CSV file into a pandas DataFrame.
   
2. **Transform:**

   * Convert columns to proper dtypes.
   * Trim whitespace and normalize text.
   * Round key decimal fields to 2 decimal points.
   * Impute missing “Flag” columns as `"No"` and other string columns as `"Unknown"`.
   * Drop rows with any negative integer attributes.
   * Remove fully duplicate rows
     
3. **Load:**

   * Write unique addresses into `Address_info` and capture their Auto-generated primary key IDs.
   * Write unique properties (linking to `Address_ID`) into `Property` table and capture their Auto-generated primary key IDs.
   * Insert those `Property_ID` values into each child DataFrame (`Leads`, `Valuation`, `Rehab`, `HOA`, `Taxes`) and bulk insert.

### Approach & Design


1. **Modular functions**

- **`extract()`** reads the CSV.  
- **`transform()`** applies all cleaning, filling missing data and other transformations.  
- **`insert_address_data_to_mysql()`** & **`insert_property_data_to_mysql()`** perform row-by-row inserts, and retrive `lastrowid` for surrogate keys.  
- **`insert_to_mysql()`** bulk-inserts any table once its DataFrame is ready into MYSQL.  
- **`load_data()`** ties everything together for loading transformed data: building the DataFrames, mapping primary key IDs, and calling the insert functions for multiple tables.  

2. **Type safety**

   * We convert pandas’ nullable `Int64`/`Float64` to native Python types before inserting data to MYSQL.
     
3. **Error handling**

   * Each insert function catches and logs any `mysql.connector.Error`, so failures are visible without crashing the entire run.


### How to Run ETL script

1. **Ensure your database is ready**

   ```bash
   docker-compose -f docker-compose.final.yml up --build -d
   ```

   * Wait until MySQL reports “ready for connections.”

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Your `requirements.txt` includes:

   ```text
   pandas
   mysql-connector-python
   ```

4. **Configure connection**
   In `etl.py` (or via environment variables), set:

   ```python
   DB_CONFIG = {
       "host":     "127.0.0.1",
       "port":     3306,
       "user":     "db_user",
       "password": "6equj5_db_user",
       "database": "home_db"
   }
   CSV_FILE_PATH = "sql/fake_data.csv"
   ```

5. **Run the ETL**

   ```bash
   python etl.py
   ```

   You should see console output.


### Requirements

* **Python 3.8+**
* **pandas** (for DataFrame operations)
* **mysql-connector-python** (for connecting to MySQL)
* **Docker & docker-compose** (to spin up the MySQL instance)

With those in place, you can repeatably run the ETL end-to-end, transforming the raw CSV into a fully normalized, relational MySQL database.


---

## Submission Guidelines

- Edit this README with your solutions and instructions for each section
- Place all scripts/code in their respective folders (`sql/`, `scripts/`, etc.)
- Ensure all steps are fully **reproducible** using your documentation

---

**Good luck! We look forward to your submission.**
