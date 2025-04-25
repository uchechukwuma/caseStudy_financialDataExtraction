# Company Financial Data Extractor

Extracts financial data for companies from Yahoo Finance API for the most recent 5 years.

## Features
- Retrieves revenue data for 100+ companies
- Validates and cleans financial data
- Outputs to properly formatted Excel files

## Usage
1. Install requirements: `pip install -r requirements.txt`
2. Run: `python case_study_test.py`
3. Output will be saved to `company_financials.xlsx`

## Data Columns
- timevalue: Year (2020-2024)
- companyname: Official company name
- revenue: Annual revenue (positive integers only)
- revenue_unit: Currency (typically USD)

## Detailed Installation
   
   1. **Prerequisites**:
      - Python 3.8+
      - [Optional] Virtual environment
   
   2. **Setup**:
      ```bash
      python -m venv venv
      source venv/bin/activate  # Windows: venv\Scripts\activate
      pip install -r requirements.txt
      ```
   
   3. **Configuration**:
      [YFinance-specific: Rate limiting notes]
   
   4. **Execution**:
      ```bash
      python src/[approach]_extractor.py
      ```

## 🧑‍💻 Author
Uchechukwu Obi
www.linkedin.com/in/uchechukwu-obi-683045347