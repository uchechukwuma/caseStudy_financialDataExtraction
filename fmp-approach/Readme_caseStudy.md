# 📊 Company Financials Data Extraction – Python Case Study

This project extracts company financial data from the [Financial Modeling Prep API](https://financialmodelingprep.com/) and loads it into an Excel file in a pre-defined format.

It was developed as part of a case study task focused on **data sourcing and transformation using Python**.


## 📦 Project Structure

company-financials-case-study/ 
├── data/ 
│ └── company_financials.xlsx # Final output file (generated) │ ├── src/ 
│ └── extract_financials.py # Main Python script │ ├── .env.example # Template for environment variables ├── .gitignore # To keep sensitive files out of Git 
├── requirements.txt # Python dependencies 
├── README.md # This file
├──company_symbols


## 🔧 Features

- Extracts financial data for 100–500 companies (edit list as needed)
- Retrieves the most recent **5 years** of revenue data per company
- Uses industry classification and country info
- Outputs to Excel in the provided format
- Cleaned and formatted for easy analysis
- Logs progress and errors with built-in `logging`
- Securely handles API credentials with a `.env` file

---

## 🚀 How to Run

### 1. 📥 Clone the Repository
```bash
git clone https://github.com/your-username/company-financials-case-study.git
cd company-financials-case-study

### 2. 🧪 Create a .env File
Create a .env file in the root directory and paste in your API key:

API_KEY=your_api_key_here

*You can get a free API key by signing up at Financial Modeling Prep.


### 3. 📦 Install Required Libraries
It's best to use a virtual environment:

python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt

### 4. 🧠 Run the Script

python src/extract_financials.py

This will:

Fetch data for selected companies

Save the result to data/company_financials.xlsx

🧾 Sample Output

timevalue| companyname	| industryclassification | geonameen 	| revenue	    | revenue_unit
2024	 |Apple Inc.	|Consumer Electronics	 |United States	|394328000000	|USD
🔐 Environment Variables
This project uses environment variables to keep your API key safe.

.env.example is included as a template.

.env is ignored via .gitignore and should be created manually.

### 📚 Requirements
Python 3.8+

Internet connection (for API calls)

requirements.txt includes:

pandas

requests

openpyxl

python-dotenv

### 💡 Customization
You can:

Add more tickers to the tickers list in extract_financials.py

Modify output format or fields

Connect to a database or cloud store instead of Excel

### 🛠 Troubleshooting

| Error | Solution |
|-------|----------|
| API Limits | Add delay between requests |
| Missing .env | Copy .env.example → .env |

### 🧑‍💻 Author
Uchechukwu Obi
www.linkedin.com/in/uchechukwu-obi-683045347

### 📄 License
This project is for demonstration purposes.