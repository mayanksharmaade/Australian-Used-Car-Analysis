Australian Used Car Analysis
Overview
Australian Used Car Analysis is an end-to-end data engineering, machine learning, and business intelligence portfolio project focused on the Australian used-car market.
The project demonstrates how raw vehicle listing data can be transformed into a structured analytics pipeline, enriched with vehicle and location information, explored through statistical analysis, used to train a price-prediction model, and finally presented through Power BI for business-facing insights.
The solution combines:
- Python-based data engineering
- SQL Server staging, curated, and warehouse layers
- Exploratory data analysis
- Feature engineering
- Machine learning model comparison and tuning
- Used-car price prediction
- Analytics dataset generation
- Power BI dashboarding
The project is designed to show the complete journey from raw data to decision-ready insight rather than focusing only on model training.
Project Objectives
The main goals of the project are to:
1. Build a reliable data pipeline for Australian used-car listings.
2. Clean and validate inconsistent raw vehicle data.
3. Enrich listings with vehicle specifications and geographic information.
4. Create curated and warehouse-ready datasets.
5. Explore pricing patterns and depreciation behaviour.
6. Engineer features suitable for machine learning.
7. Compare baseline regression models.
8. Train and evaluate a final used-car price prediction model.
9. Generate market and vehicle-level value insights.
10. Deliver business-facing dashboards through Power BI.
Technology Stack
Data Engineering and Analytics
- Python 3.11 / 3.12
- pandas
- NumPy
- SQL Server
- T-SQL
- Jupyter Notebook
Machine Learning
- scikit-learn
- Random Forest Regressor
- Linear Regression
- Median baseline model
- joblib
Business Intelligence
- Power BI Desktop

Australian-Used-Car-Analysis/
│
├── bi/
├── config/
├── data/
├── docs/
├── eda/
├── etl/
├── features/
├── ingestion/
├── ml/
├── notebooks/
├── reports/
├── scripts/
├── sql/
├── tests/
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md

Data Engineering
The project begins with multiple raw data sources, including used-car listings, Australian postcode/location data, and vehicle specification datasets.
The pipeline profiles incoming data before loading it into structured SQL Server layers.
Key data-engineering tasks include:
- Schema inspection
- Null and missing-value analysis
- Duplicate detection
- Data-type validation
- Vehicle make and model normalisation
- Geographic enrichment
- Matching vehicle listings to specification data
- Business-rule validation
- Staging-to-curated transformations
- Warehouse loading
The project separates raw ingestion from downstream analytical processing so data quality can be checked at each stage.
SQL Server Architecture
The database flow follows a layered approach:
Raw Files
   │
   ▼
stg
   │
   ▼
curated
   │
   ▼
dw
At the project checkpoint, the major row counts were approximately:
stg.CarListing             16,734
curated.CarListing         16,676
dw.FactCarListing          16,675
stg.VehicleSpecification      800
stg.Location                2,640
The reduction in rows reflects cleaning, validation, and deduplication logic applied during the pipeline.
Exploratory Data Analysis
EDA is used to understand both the market and the quality of the dataset before modelling.
The project produces structured reports for:
- Price distributions
- Make and model frequency
- Body type
- Fuel type
- Transmission
- Drive type
- Model year
- Kilometre bands
- State distribution
- Missing values
- Duplicate records
- Outliers
- Vehicle specification matching
- Location matching
- Structural anomalies
Examples of analytical questions explored include:
- Which manufacturers dominate the dataset?
- How does price vary across makes and models?
- How strongly does vehicle age influence price?
- How does mileage relate to resale value?
- Which body types command higher prices?
- How do fuel type and transmission relate to market value?
- Are there listings with implausible or structurally unusual values?
The project stores many of these outputs under reports/eda/ so the analytical process remains transparent and reproducible.
Feature Engineering
The feature engineering stage converts cleaned vehicle data into predictors suitable for machine learning.
Examples include:
- Vehicle age
- Model year
- Odometer / kilometre information
- Make
- Model
- Body type
- Transmission
- Fuel type
- Drive type
- Location-derived information
- Vehicle specification attributes
- Price-related derived fields
- Market-position features where appropriate
Categorical values are encoded as part of the model pipeline, while numerical features are prepared for consistent training and evaluation.
The final baseline training process used 21 predictors.
Machine Learning
The machine-learning phase focuses on estimating used-car prices as a supervised regression problem.
Dataset Split
At the baseline checkpoint:
Training rows:   9,973
Validation rows: 3,325
Predictors:      21
A separate test set is retained for final evaluation.
Baseline Model Comparison
Dummy Median Baseline
MAE: approximately $18,265
Linear Regression
MAE: approximately $8,522
R²:  approximately 0.495
Random Forest
MAE:  approximately $6,232
RMSE: approximately $28,275
R²:   approximately 0.534
Random Forest performed better than the simpler baselines and was selected for further tuning and final evaluation.
Final Model
The final selected model was a Random Forest with 500 trees.
Model: RF_500Trees
MAE:   approximately $6,216
R²:    approximately 0.534
The model was persisted locally as:
models/final_used_car_price_model.joblib
Model binaries are excluded from the public repository by default, while the training code, evaluation reports, and supporting metrics remain available.
The model is intended to support market analysis and vehicle value exploration rather than provide a guaranteed commercial valuation.
Model Evaluation
The project stores model-evaluation outputs including:
- Candidate model comparison
- Final test metrics
- Prediction outputs
- Feature importance
- Permutation importance
- Tuning results
- Validation predictions
These reports help explain not only which model performed best but also how the final model behaves.
Analytics Dataset
After the data engineering and ML stages, a final analytical dataset is exported for reporting and Power BI.
The project generated approximately:
16,675 rows
in:
data/analytics/used_car_market_analytics.csv
This dataset combines cleaned market data with machine-learning and analytical outputs so business users can explore pricing and value patterns without interacting directly with Python or SQL.
Power BI Dashboard
Power BI is used as the presentation layer for the project.
Page 1 — Market Overview
Focuses on high-level market composition.
Typical visuals include:
- Total listings
- Average / median price
- Make distribution
- Body-type distribution
- State-level analysis
- Interactive slicers
Page 2 — Price & Depreciation
Focuses on pricing behaviour.
Visuals include:
- Price KPIs
- Age versus price
- Kilometres versus price
- Price distribution
- Depreciation patterns
Page 3 — Make & Model Analysis
Allows deeper comparison across manufacturers and models, including a Top-25 style matrix and supporting breakdowns.
Page 4 — ML & Value Insights
Connects the machine-learning results to business-facing analysis.
This page includes model metrics and value-oriented summaries that help distinguish between actual market price and model-estimated price.
Page 5 — Vehicle Value Explorer
The planned interactive page is intended to let a user filter vehicle characteristics and explore:
- Actual listing price
- Predicted price
- Price difference
- Relative value position
- Comparable market vehicles
This brings the ML output into a form that is directly usable by a non-technical audience.
Business Use Cases
Vehicle Buyer
A buyer could compare the listed price of a vehicle against a model-estimated market value.
Dealer or Marketplace
A dealer could identify listings that appear unusually expensive or inexpensive relative to similar vehicles.
Market Analyst
An analyst could examine manufacturer pricing, depreciation trends, state-level market patterns, body-type demand, fuel-type differences, and price distributions.
Data Science Team
The project provides a reproducible pipeline from raw data through feature engineering and model evaluation.
Data Quality and Validation
Data quality is treated as a separate engineering concern rather than being hidden inside model preparation.
The repository contains outputs for:
- Missing-value summaries
- Duplicate checks
- Numeric profiling
- Categorical profiling
- Business-rule checks
- Outlier detection
- Vehicle-specification matching
- Geographic matching
- Structural anomalies
This helps explain why particular records may have been removed or transformed before reaching the machine-learning stage.
- Power Query
- DAX
- CSV-based analytical extracts
