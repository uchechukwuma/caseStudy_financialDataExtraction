import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

# === CONFIGURATION SETUP ===
load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"
MAX_COMPANIES = int(os.getenv("MAX_COMPANIES", 120))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
BASE_DELAY = float(os.getenv("BASE_DELAY", 0.1))
YEARS = 5   # Number of years to fetch income statements for

# === LOGGING CONFIGURATION ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_data_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === DEFAULT COMPANY LIST ===
DEFAULT_COMPANIES = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JPM", "V", 
    "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "BAC", "PYPL", "CMCSA", 
    "XOM", "NFLX", "PFE", "VZ", "ADBE", "CRM", "CSCO", "PEP", "KO", "T", 
    "ABT", "AVGO", "COST", "MRK", "DHR", "MCD", "ABBV", "TMO", "ACN", "NKE", 
    "PM", "LIN", "ORCL", "AMD", "IBM", "QCOM", "INTU", "AMGN", "HON", "CAT", 
    "GE", "MMM", "BA", "GS", "LOW", "SBUX", "MDT", "UPS", "CVX", "DE", 
    "RTX", "SCHW", "BLK", "AXP", "PLD", "NOW", "AMT", "TXN", "BKNG", "ADI", 
    "GILD", "LMT", "CVS", "CI", "MO", "SPGI", "SYK", "ZTS", "REGN", "MDLZ", 
    "TMUS", "FISV", "VRTX", "ISRG", "MU", "EQIX", "ILMN", "ATVI", "KLAC", 
    "MNST", "ADP", "CSX", "MAR", "PANW", "SNPS", "CDNS", "CHTR", "APH", "MCO"
]

def load_company_symbols():
    """Load company symbols from file if available, otherwise fallback to default list."""
    try:
        with open("company_symbols.txt") as f:
            symbols = [line.strip() for line in f if line.strip()]
            if symbols:
                logger.info(f"Loaded {len(symbols)} symbols from file.")
                return symbols
    except FileNotFoundError:
        logger.warning("company_symbols.txt not found. Using default list.")

    logger.info(f"Using {len(DEFAULT_COMPANIES)} default companies.")
    return DEFAULT_COMPANIES


class FinancialDataExtractor:
    def __init__(self):
        self.data = []
        self.processed_symbols = set()
        self.failed_symbols = set()
        self.request_count = 0

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        before_sleep=lambda r: logger.warning(
            f"Retrying after failure: {r.outcome.exception()}")
    )
    def _fetch_api_data(self, url):
        """
        Makes an HTTP GET request to the API with retry logic.
        """
        headers = {
            "User-Agent": "FinancialDataExtractor/1.0",
            "Accept": "application/json"
        }
        self.request_count += 1
        if self.request_count % 10 == 0:
            time.sleep(BASE_DELAY)

        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, (list, dict)):
            raise ValueError("Unexpected API response format")
        return data

    def get_company_profile(self, symbol):
        """Fetches the company profile details for a symbol."""
        url = f"{BASE_URL}/profile/{symbol}?apikey={API_KEY}"
        result = self._fetch_api_data(url)
        return result[0] if result and isinstance(result, list) else None

    def get_income_statement(self, symbol):
        """Fetches the last few years of income statement data."""
        url = f"{BASE_URL}/income-statement/{symbol}?limit={YEARS}&apikey={API_KEY}"
        return self._fetch_api_data(url)

    def _extract_fiscal_year(self, statement):
        """Extracts the fiscal year from income statement entry."""
        if fiscal_year := statement.get("fiscalYear"):
            return str(fiscal_year)
        if date_str := statement.get("date"):
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y")
            except ValueError:
                return "N/A"
        return "N/A"

    def _process_revenue(self, revenue):
        """
        Cleans and converts revenue value to integer,
        handling scientific notation and invalid formats.
        """
        try:
            revenue_val = int(float(revenue))
            return revenue_val if revenue_val >= 0 else None
        except (ValueError, TypeError):
            return None

    def extract_company_data(self, symbol):
        """
        Pulls and processes financial data for a single company.
        Adds clean entries to the internal dataset.
        """
        if symbol in self.processed_symbols:
            return

        try:
            logger.info(f"Processing {symbol}")
            profile = self.get_company_profile(symbol)
            if not profile:
                raise ValueError("Missing company profile")

            statements = self.get_income_statement(symbol)
            if not statements or not isinstance(statements, list):
                raise ValueError("Missing income statement data")

            for statement in statements:
                revenue = self._process_revenue(statement.get("revenue"))
                if revenue is None:
                    continue

                self.data.append({
                    "timevalue": self._extract_fiscal_year(statement),
                    "companyname": profile.get("companyName", "N/A"),
                    "industryclassification": profile.get("industry", "N/A"),
                    "geonameen": profile.get("country", "N/A"),
                    "revenue": revenue,
                    "revenue_unit": statement.get("reportedCurrency", "USD")
                })

            self.processed_symbols.add(symbol)

        except Exception as e:
            self.failed_symbols.add(symbol)
            logger.error(f"Failed to process {symbol}: {e}")

    def extract_all_companies(self, symbols):
        """
        Iterates through a list of symbols and collects data
        until the defined limit is reached.
        """
        valid_symbols = []
        for symbol in symbols:
            if len(valid_symbols) >= MAX_COMPANIES:
                break
            before = len(self.data)
            self.extract_company_data(symbol)
            after = len(self.data)
            if after > before:
                valid_symbols.append(symbol)
        logger.info(f"Successfully collected data for {len(valid_symbols)} companies.")

    def export_to_excel(self, filename="company_financial_data.xlsx"):
        """
        Exports the cleaned financial data to an Excel file.
        """
        if not self.data:
            logger.warning("No data to export.")
            return False

        try:
            df = pd.DataFrame(self.data)
            df = df.drop_duplicates()
            df = df[df['timevalue'] != "N/A"]
            df = df[df['revenue'].notna()]
            df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').astype('Int64')
            df = df.sort_values(['companyname', 'timevalue'], ascending=[True, False])

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                writer.sheets['Sheet1'].freeze_panes = 'A2'

            logger.info(f"Exported {len(df)} records to {filename}")
            if self.failed_symbols:
                logger.warning(f"Failed symbols: {', '.join(self.failed_symbols)}")
            return True

        except Exception as e:
            logger.error(f"Excel export failed: {e}", exc_info=True)
            return False


def main():
    """
    Main execution flow:
    Loads symbols, fetches data, and exports it.
    """
    logger.info("Starting financial data extraction")
    extractor = FinancialDataExtractor()
    symbols = load_company_symbols()

    if not symbols:
        logger.error("No company symbols found.")
        return

    extractor.extract_all_companies(symbols)

    if not extractor.export_to_excel():
        logger.error("Data export failed.")
    else:
        logger.info("Data export completed successfully.")


if __name__ == "__main__":
    main()
