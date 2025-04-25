# Company Financial Data Extraction - Dual Approach

This project demonstrates two different methods for extracting company financial data:

## 🔧 Available Approaches

1. **[Yahoo Finance API](yfinance-approach/)** - Direct scraping approach
   - No API key required
   - Good for quick prototyping
   - Limited historical data

2. **[Financial Modeling Prep API](fmp-approach/)** - Professional financial API
   - More reliable data
   - Requires free API key(API LIMIT applies)
   - Better for production use

## 📊 Sample Output
See [documents/SAMPLE_OUTPUT.xlsx](docs/SAMPLE_OUTPUT.xlsx) for the expected format

## 🏗 Project Structure
company-financials-case-study/
├── yfinance-approach/                # First approach using Yahoo Finance
│   ├── src/
│   │   └── case_study_financialData.py     # Main script
│   ├── case_study_financialData.txt        # Specific to yfinance
│   └── README.md                     # Specific docs
│
├── fmp-approach/                     # Second approach using Financial Modeling Prep
│   ├── src/
│   │   └── fmp_extractor.py          # Main script
│   ├── requirements.txt              # Specific to FMP
│   ├── .env.example                  # API key template
│   ├── README.md                     # Specific docs
│   └── company_symbols
│
├── documents/                             # Common documentation
│   ├── COMPARISON.md                 # Comparison of both approaches
│   └── SAMPLE_OUTPUT.xlsx            # Example output file
│
├── .gitignore                        # Combined ignore rules
├── README.md                         # Main project overview
└── Company_Background                # Overview of covered companies

## 🚀 Quick Deployment

### For Yahoo Finance Approach:
```bash
cd yfinance-approach
pip install -r requirements.txt
python src/yfinance_extractor.py

### For FMP Approach:
```bash
cd fmp-approach
cp .env.example .env  # Add your API key first!
pip install -r requirements.txt
python src/fmp_extractor.py
See each approach's dedicated README for detailed instructions.

## 🛠 Troubleshooting

| Error | Solution |
|-------|----------|
| API Limits | Add delay between requests |
| Missing .env | Copy .env.example → .env |

## 🧑‍💻 Author
Uchechukwu Obi  
[LinkedIn Profile](www.linkedin.com/in/uchechukwu-obi-683045347)