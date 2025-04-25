import pandas as pd
import yfinance as yf
from tqdm import tqdm
import time
import sys
import subprocess


# === CONFIGURATION ===
OUTPUT_FILE = 'company_financials.xlsx'
YEARS = [2024, 2023, 2022, 2021, 2020]  # Most recent 5 years
CURRENT_YEAR = 2024

def safe_yfinance_call(ticker):
    """Wrapper with error handling for yfinance"""
    try:
        return yf.Ticker(ticker)
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

def get_financial_data(ticker_map):
    """Attempts multiple methods to extract revenue for a specific year"""
    results = []
    
    for ticker, company_name in tqdm(ticker_map.items(), desc="Processing Companies"):
        try:
            company = safe_yfinance_call(ticker)
            if not company:
                continue
                
            info = company.info
            financials = company.financials  # Annual financials
            quarterly = company.quarterly_financials  # Quarterly financials
            
            for year in YEARS:
                revenue = None
                revenue_source = None  
                
                # Method 1:  Annual Financials
                if financials is not None and not financials.empty:
                    for col in financials.columns:
                        if str(year) in str(col):
                            if not financials[col].empty:
                                revenue = financials[col].iloc[0]
                                revenue_source = "annual report"
                            break
                
                # Method 2:  Quarterly Sum (only for current year)
                if revenue is None and year == CURRENT_YEAR and quarterly is not None:
                    current_year_cols = [col for col in quarterly.columns if str(year) in str(col)]
                    if current_year_cols:
                        revenue = quarterly[current_year_cols].sum().sum()
                        revenue_source = "quarterly reports"
                
                # Method 3: Fallback to info dictionary
                if revenue is None:
                    if year == CURRENT_YEAR and 'totalRevenue' in info:
                        revenue = info['totalRevenue']
                        revenue_source = "company info"
                    elif f'revenue{year}' in str(info).lower():
                        for k, v in info.items():
                            if str(year) in str(k) and 'revenue' in str(k).lower():
                                revenue = v
                                revenue_source = "company info"
                                break
                
                if revenue is not None:
                    """Ensures revenue is a valid positive integer"""
                    try:
                        # Convert to integer
                        revenue_int = int(float(revenue))
                        
                        # Revenue validation
                        if revenue_int < 0:
                            print(f"Warning: Negative revenue ({revenue_int}) for {company_name} ({year}) from {revenue_source} - treating as unavailable")
                            continue
                        elif revenue_int == 0:
                            print(f"Warning: Zero revenue for {company_name} ({year}) from {revenue_source} - treating as unavailable")
                            continue
                            
                        results.append({
                            'timevalue': str(year),
                            'companyname': company_name,
                            'industryclassification': info.get('industry', info.get('sector', 'N/A')),
                            'geonameen': info.get('country', 'N/A'),
                            'revenue': revenue_int, 
                            'revenue_unit': info.get('currency', 'USD'),
                            'data_source': revenue_source  
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Error converting revenue for {company_name} ({year}): {str(e)}")
                        continue
            
            time.sleep(0.5)  
            
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            continue
    
    return pd.DataFrame(results)

# ticker map [Selected 500 companies]
ticker_map = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc.",
    "BRK-B": "Berkshire Hathaway Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "WMT": "Walmart Inc.",
    "PG": "Procter & Gamble Company",
    "JNJ": "Johnson & Johnson",
    "XOM": "Exxon Mobil Corporation",
    "HD": "Home Depot Inc.",
    "MA": "Mastercard Incorporated",
    "DIS": "Walt Disney Company",
    "PEP": "PepsiCo Inc.",
    "KO": "Coca-Cola Company",
    "ABBV": "AbbVie Inc.",
    "PFE": "Pfizer Inc.",
    "MRK": "Merck & Co. Inc.",
    "TMO": "Thermo Fisher Scientific Inc.",
    "AVGO": "Broadcom Inc.",
    "COST": "Costco Wholesale Corporation",
    "CRM": "Salesforce Inc.",
    "NFLX": "Netflix Inc.",
    "ADBE": "Adobe Inc.",
    "PYPL": "PayPal Holdings Inc.",
    "INTC": "Intel Corporation",
    "AMD": "Advanced Micro Devices Inc.",
    "QCOM": "Qualcomm Incorporated",
    "CSCO": "Cisco Systems Inc.",
    "CMCSA": "Comcast Corporation",
    "T": "AT&T Inc.",
    "VZ": "Verizon Communications Inc.",
    "UNH": "UnitedHealth Group Incorporated",
    "BAC": "Bank of America Corporation",
    "WFC": "Wells Fargo & Company",
    "GS": "Goldman Sachs Group Inc.",
    "NKE": "Nike Inc.",
    "SBUX": "Starbucks Corporation",
    "MDT": "Medtronic plc",
    "BMY": "Bristol-Myers Squibb Company",
    "ABT": "Abbott Laboratories",
    "DHR": "Danaher Corporation",
    "LIN": "Linde plc",
    "RTX": "Raytheon Technologies Corporation",
    "HON": "Honeywell International Inc.",
    "LOW": "Lowe's Companies Inc.",
    "UPS": "United Parcel Service Inc.",
    "CAT": "Caterpillar Inc.",
    "DE": "Deere & Company",
    "MMM": "3M Company",
    "GE": "General Electric Company",
    "BA": "Boeing Company",
    "UNP": "Union Pacific Corporation",
    "IBM": "International Business Machines Corporation",
    "TXN": "Texas Instruments Incorporated",
    "NOW": "ServiceNow Inc.",
    "INTU": "Intuit Inc.",
    "AMGN": "Amgen Inc.",
    "GILD": "Gilead Sciences Inc.",
    "ISRG": "Intuitive Surgical Inc.",
    "VRTX": "Vertex Pharmaceuticals Incorporated",
    "REGN": "Regeneron Pharmaceuticals Inc.",
    "MRNA": "Moderna Inc.",
    "LLY": "Eli Lilly and Company",
    "DASH": "DoorDash Inc.",
    "UBER": "Uber Technologies Inc.",
    "ZM": "Zoom Video Communications Inc.",
    "SHOP": "Shopify Inc.",
    "SQ": "Block Inc.",
    "SNOW": "Snowflake Inc.",
    "MDB": "MongoDB Inc.",
    "DDOG": "Datadog Inc.",
    "NET": "Cloudflare Inc.",
    "CRWD": "CrowdStrike Holdings Inc.",
    "ZS": "Zscaler Inc.",
    "TEAM": "Atlassian Corporation",
    "OKTA": "Okta Inc.",
    "DOCU": "DocuSign Inc.",
    "TWLO": "Twilio Inc.",
    "FSLY": "Fastly Inc.",
    "PLTR": "Palantir Technologies Inc.",
    "ASAN": "Asana Inc.",
    "COIN": "Coinbase Global Inc.",
    "HOOD": "Robinhood Markets Inc.",
    "RBLX": "Roblox Corporation",
    "PINS": "Pinterest Inc.",
    "SNAP": "Snap Inc.",
    "SPOT": "Spotify Technology S.A.",
    "LYFT": "Lyft Inc.",
    "ABNB": "Airbnb Inc.",
    "BKNG": "Booking Holdings Inc.",
    "EXPE": "Expedia Group Inc.",
    "TRIP": "Tripadvisor Inc.",
    "MAR": "Marriott International Inc.",
    "HLT": "Hilton Worldwide Holdings Inc.",
    "DAL": "Delta Air Lines Inc.",
    "AAL": "American Airlines Group Inc.",
    "UAL": "United Airlines Holdings Inc.",
    "LUV": "Southwest Airlines Co.",
    "CCL": "Carnival Corporation & plc",
    "RCL": "Royal Caribbean Cruises Ltd.",
    "NCLH": "Norwegian Cruise Line Holdings Ltd.",
    "MGM": "MGM Resorts International",
    "WYNN": "Wynn Resorts Limited",
    "LVS": "Las Vegas Sands Corp.",
    "CZR": "Caesars Entertainment Inc.",
    "PENN": "Penn National Gaming Inc.",
    "DKNG": "DraftKings Inc.",
    "FVRR": "Fiverr International Ltd.",
    "UPWK": "Upwork Inc.",
    "ETSY": "Etsy Inc.",
    "W": "Wayfair Inc.",
    "CHWY": "Chewy Inc.",
    "PTON": "Peloton Interactive Inc.",
    "NIO": "NIO Inc.",
    "LI": "Li Auto Inc.",
    "XPEV": "XPeng Inc.",
    "LCID": "Lucid Group Inc.",
    "RIVN": "Rivian Automotive Inc.",
    "FSR": "Fisker Inc.",
    "NKLA": "Nikola Corporation",
    "GOEV": "Canoo Inc.",
    "ARVL": "Arrival",
    "PSNY": "Polestar Automotive Holding UK PLC",
    "SOLO": "Electrameccanica Vehicles Corp. Ltd.",
    "WKHS": "Workhorse Group Inc.",
    "RIDE": "Lordstown Motors Corp.",
    "SBEV": "Splash Beverage Group Inc.",
    "CELH": "Celsius Holdings Inc.",
    "MNST": "Monster Beverage Corporation",
    "KDP": "Keurig Dr Pepper Inc.",
    "STZ": "Constellation Brands Inc.",
    "BUD": "Anheuser-Busch InBev SA/NV",
    "TAP": "Molson Coors Beverage Company",
    "SAM": "Boston Beer Company Inc.",
    "BYND": "Beyond Meat Inc.",
    "TTCF": "Tattooed Chef Inc.",
    "APPH": "AppHarvest Inc.",
    "BROS": "Dutch Bros Inc.",
    "JACK": "Jack in the Box Inc.",
    "DNUT": "Krispy Kreme Inc.",
    "SHAK": "Shake Shack Inc.",
    "CMG": "Chipotle Mexican Grill Inc.",
    "DPZ": "Domino's Pizza Inc.",
    "YUM": "Yum! Brands Inc.",
    "QSR": "Restaurant Brands International Inc.",
    "MCD": "McDonald's Corporation",
    "SBUX": "Starbucks Corporation",
    "DRI": "Darden Restaurants Inc.",
    "BLMN": "Bloomin' Brands Inc.",
    "EAT": "Brinker International Inc.",
    "DIN": "Dine Brands Global Inc.",
    "DENN": "Denny's Corporation",
    "ARCO": "Arcos Dorados Holdings Inc.",
    "PZZA": "Papa John's International Inc.",
    "WING": "Wingstop Inc.",
    "LIND": "Lindblad Expeditions Holdings Inc.",
    "LIVN": "LivaNova PLC",
    "LJPC": "La Jolla Pharmaceutical Company",
    "LKCO": "Luokung Technology Corp.",
    "LMAT": "LeMaitre Vascular Inc.",
    "LMPX": "LMP Automotive Holdings Inc.",
    "LNTH": "Lantheus Holdings Inc.",
    "LPCN": "Lipocine Inc.",
    "LQDA": "Liquidia Corporation",
    "LRMR": "Larimar Therapeutics Inc.",
    "LTRN": "Lantern Pharma Inc.",
    "LTRX": "Lantronix Inc.",
    "LUCD": "Lucid Diagnostics Inc.",
    "LUMO": "Lumos Pharma Inc.",
    "LUNG": "Pulmonx Corporation",
    "LXRX": "Lexicon Pharmaceuticals Inc.",
    "LYEL": "Lyell Immunopharma Inc.",
    "MACK": "Merrimack Pharmaceuticals Inc.",
    "MAGS": "Magal Security Systems Ltd.",
    "MARK": "Remark Holdings Inc.",
    "MNPR": "Monopar Therapeutics Inc.",
    "MNRO": "Monro Inc.",
    "MODV": "ModivCare Inc.",
    "MORF": "Morphic Holding Inc.",
    "MOTS": "Motus GI Holdings Inc.",
    "MRAM": "Everspin Technologies Inc.",
    "MRNS": "Marinus Pharmaceuticals Inc.",
    "MRSN": "Mersana Therapeutics Inc.",
    "MRUS": "Merus N.V.",
    "MSON": "MISONIX Inc.",
    "MTEM": "Molecular Templates Inc.",
    "MTEX": "Mannatech Incorporated",
    "MTNB": "Matinas BioPharma Holdings Inc.",
    "MUDS": "Mudrick Capital Acquisition Corporation II",
    "NRC": "National Research Corporation",
    "NRBO": "NeuroBo Pharmaceuticals Inc.",
    "NSSC": "NAPCO Security Technologies Inc.",
    "NTEC": "Intec Pharma Ltd.",
    "NTGR": "NETGEAR Inc.",
    "NTIC": "Northern Technologies International Corporation",
    "NTLA": "Intellia Therapeutics Inc.",
    "NTRA": "Natera Inc.",
    "NTRS": "Northern Trust Corporation",
    "NURO": "NeuroMetrix Inc.",
    "NUVA": "NuVasive Inc.",
    "NVAX": "Novavax Inc.",
    "NVCN": "Neovasc Inc.",
    "NVCR": "NovoCure Limited",
    "NVFY": "Nova Lifestyle Inc.",
    "NVTA": "Invitae Corporation",
    "NWLI": "National Western Life Group Inc.",
    "NXTC": "NextCure Inc.",
    "NYMT": "New York Mortgage Trust Inc.",
    "OBSV": "ObsEva SA",
    "OCUL": "Ocular Therapeutix Inc.",
    "ODP": "ODP Corporation",
    "OESX": "Orion Energy Systems Inc.",
    "OFIX": "Orthofix Medical Inc.",
    "OGI": "Organigram Holdings Inc.",
    "OM": "Outset Medical Inc.",
    "OMER": "Omeros Corporation",
    "ONCY": "Oncolytics Biotech Inc.",
    "ONEM": "1Life Healthcare Inc.",
    "ONTX": "Onconova Therapeutics Inc.",
    "OPK": "OPKO Health Inc.",
    "OPRT": "Oportun Financial Corporation",
    "ORMP": "Oramed Pharmaceuticals Inc.",
    "ORPH": "Orphazyme A/S",
    "OSMT": "Osmotica Pharmaceuticals plc",
    "OSUR": "OraSure Technologies Inc.",
    "OTIC": "Otonomy Inc.",
    "OTLK": "Outlook Therapeutics Inc.",
    "OTTR": "Otter Tail Corporation",
    "OVLY": "Oak Valley Bancorp",
    "OXBR": "Oxbridge Re Holdings Limited",
    "OXSQ": "Oxford Square Capital Corp.",
    "PAHC": "Phibro Animal Health Corporation",
    "PAVM": "PAVmed Inc.",
    "PBYI": "Puma Biotechnology Inc.",
    "PCYG": "Park City Group Inc.",
    "PDEX": "Pro-Dex Inc.",
    "PFMT": "Performant Financial Corporation",
    "PGEN": "Precigen Inc.",
    "PHAT": "Phathom Pharmaceuticals Inc.",
    "PHUN": "Phunware Inc.",
    "PIRS": "Pieris Pharmaceuticals Inc.",
    "PLSE": "Pulse Biosciences Inc.",
    "PMVP": "PMV Pharmaceuticals Inc.",
    "PNTG": "The Pennant Group Inc.",
    "PRQR": "ProQR Therapeutics N.V.",
    "PRTA": "Prothena Corporation plc",
    "PRTH": "Priority Technology Holdings Inc.",
    "PTCT": "PTC Therapeutics Inc.",
    "PTGX": "Protagonist Therapeutics Inc.",
    "PTVE": "Pactiv Evergreen Inc.",
    "PUMP": "ProPetro Holding Corp.",
    "PVAC": "Penn Virginia Corporation",
    "QDEL": "Quidel Corporation",
    "QNST": "QuinStreet Inc.",
    "QURE": "uniQure N.V.",
    "RAPT": "RAPT Therapeutics Inc.",
    "RARE": "Ultragenyx Pharmaceutical Inc.",
    "RBCN": "Rubicon Technology Inc.",
    "RCEL": "Avita Medical Inc.",
    "RCKT": "Rocket Pharmaceuticals Inc.",
    "RCUS": "Arcus Biosciences Inc.",
    "RDHL": "Redhill Biopharma Ltd.",
    "RDNT": "RadNet Inc.",
    "REFR": "Research Frontiers Incorporated",
    "REPL": "Replimune Group Inc.",
    "RETA": "Reata Pharmaceuticals Inc.",
    "REXN": "Rexahn Pharmaceuticals Inc.",
    "RGEN": "Repligen Corporation",
    "RIGL": "Rigel Pharmaceuticals Inc.",
    "RNAC": "Cartesian Therapeutics Inc.",
    "RNGR": "Ranger Energy Services Inc.",
    "RNWK": "RealNetworks Inc.",
    "RPTX": "Repare Therapeutics Inc.",
    "RUBY": "Rubius Therapeutics Inc.",
    "RUSHA": "Rush Enterprises Inc.",
    "RUTH": "Ruth's Hospitality Group Inc.",
    "RVNC": "Revance Therapeutics Inc.",
    "RWLK": "ReWalk Robotics Ltd.",
    "RYTM": "Rhythm Pharmaceuticals Inc.",
    "SAGE": "Sage Therapeutics Inc.",
    "SAVA": "Cassava Sciences Inc.",
    "SBBP": "Strongbridge Biopharma plc",
    "SBT": "Sterling Bancorp Inc.",
    "SCPH": "scPharmaceuticals Inc.",
    "SCPL": "SciPlay Corporation",
    "SCPS": "Scopus BioPharma Inc.",
    "SCWX": "SecureWorks Corp.",
    "SDGR": "Schrödinger Inc.",
    "SEEL": "Seelos Therapeutics Inc.",
    "SELB": "Selecta Biosciences Inc.",
    "SENS": "Senseonics Holdings Inc.",
    "SESN": "Sesen Bio Inc.",
    "SFIX": "Stitch Fix Inc.",
    "SGMO": "Sangamo Therapeutics Inc.",
    "SGRY": "Surgery Partners Inc.",
    "SHC": "Sotera Health Company",
    "SHIP": "Seanergy Maritime Holdings Corp.",
    "SIBN": "SI-BONE Inc.",
    "SIGA": "SIGA Technologies Inc.",
    "SILK": "Silk Road Medical Inc.",
    "SINT": "Sintx Technologies Inc.",
    "SKIN": "The Beauty Health Company",
    "SLDB": "Solid Biosciences Inc.",
    "SLGL": "Sol-Gel Technologies Ltd.",
    "SLNO": "Soleno Therapeutics Inc.",
    "SLP": "Simulations Plus Inc.",
    "SMED": "Sharps Compliance Corp.",
    "SMMT": "Summit Therapeutics Inc.",
    "SNBR": "Sleep Number Corporation",
    "SNCE": "Science 37 Holdings Inc.",
    "SNCR": "Synchronoss Technologies Inc.",
    "SNES": "SenesTech Inc.",
    "SNGX": "Soligenix Inc.",
    "SNOA": "Sonoma Pharmaceuticals Inc.",
    "SNPX": "Synaptogenix Inc.",
    "SNSE": "Sensei Biotherapeutics Inc.",
    "SOLY": "Soliton Inc.",
    "SONM": "Sonim Technologies Inc.",
    "SONN": "Sonnet BioTherapeutics Holdings Inc.",
    "SPCB": "SuperCom Ltd.",
    "SPFI": "South Plains Financial Inc.",
    "SPNE": "SeaSpine Holdings Corporation",
    "SPNS": "Sapiens International Corporation N.V.",
    "SPPI": "Spectrum Pharmaceuticals Inc.",
    "SPRO": "Spero Therapeutics Inc.",
    "SPRT": "Support.com Inc.",
    "SPSC": "SPS Commerce Inc.",
    "SPWH": "Sportsman's Warehouse Holdings Inc.",
    "SPWR": "SunPower Corporation",
    "SQBG": "Sequential Brands Group Inc.",
    "SRNE": "Sorrento Therapeutics Inc.",
    "SRPT": "Sarepta Therapeutics Inc.",
    "SRRA": "Sierra Oncology Inc.",
    "SRRK": "Scholar Rock Holding Corporation",
    "SRTS": "Sensus Healthcare Inc.",
    "SSKN": "Strata Skin Sciences Inc.",
    "SSP": "E.W. Scripps Company",
    "SSSS": "Sutter Rock Capital Corp.",
    "STAA": "STAAR Surgical Company",
    "STAF": "Staffing 360 Solutions Inc.",
    "STIM": "Neuronetics Inc.",
    "STKL": "SunOpta Inc.",
    "STKS": "The ONE Group Hospitality Inc.",
    "STOK": "Stoke Therapeutics Inc.",
    "STRO": "Sutro Biopharma Inc.",
    "STRS": "Stratus Properties Inc.",
    "STTK": "Shattuck Labs Inc.",
    "SUPN": "Supernus Pharmaceuticals Inc.",
    "SURF": "Surface Oncology Inc.",
    "SVRA": "Savara Inc.",
    "SWAV": "ShockWave Medical Inc.",
    "SWBI": "Smith & Wesson Brands Inc.",
    "SWTX": "SpringWorks Therapeutics Inc.",
    "SXTC": "China SXT Pharmaceuticals Inc.",
    "SYBX": "Synlogic Inc.",
    "SYRS": "Syros Pharmaceuticals Inc.",
    "TAST": "Carrols Restaurant Group Inc.",
    "TBPH": "Theravance Biopharma Inc.",
    "TC": "TuanChe Limited",
    "TCON": "TRACON Pharmaceuticals Inc.",
    "TCRR": "TCR2 Therapeutics Inc.",
    "TCX": "Tucows Inc.",
    "TELA": "TELA Bio Inc.",
    "TENX": "Tenax Therapeutics Inc.",
    "TGTX": "TG Therapeutics Inc.",
    "TH": "Target Hospitality Corp.",
    "THMO": "ThermoGenesis Holdings Inc.",
    "THRX": "Theseus Pharmaceuticals Inc.",
    "TIGO": "Millicom International Cellular S.A.",
    "TIPT": "Tiptree Inc.",
    "TITN": "Titan Machinery Inc.",
    "TLC": "Taiwan Liposome Company Ltd.",
    "TLGT": "Teligent Inc.",
    "TLIS": "Talis Biomedical Corporation",
    "TLRY": "Tilray Brands Inc.",
    "TMDI": "Titan Medical Inc.",
    "TMDX": "TransMedics Group Inc.",
    "TMST": "TimkenSteel Corporation",
    "TNDM": "Tandem Diabetes Care Inc.",
    "TNXP": "Tonix Pharmaceuticals Holding Corp.",
    "TOUR": "Tuniu Corporation",
    "TPIC": "TPI Composites Inc.",
    "TPST": "Tempest Therapeutics Inc.",
    "TRHC": "Tabula Rasa HealthCare Inc.",
    "TRIB": "Trinity Biotech plc",
    "TRIL": "Trillium Therapeutics Inc.",
    "TRIN": "Trinity Capital Inc.",
    "TRIP": "Tripadvisor Inc.",
    "TRMB": "Trimble Inc.",
    "TRMD": "TORM plc",
    "TRNS": "Transcat Inc.",
    "TROX": "Tronox Holdings plc",
    "TRS": "TriMas Corporation",
    "TRST": "TrustCo Bank Corp NY",
    "TRUE": "TrueCar Inc.",
    "TRUP": "Trupanion Inc.",
    "TRVG": "trivago N.V.",
    "TRVI": "Trevi Therapeutics Inc.",
    "TSBK": "Timberland Bancorp Inc.",
    "TSC": "TriState Capital Holdings Inc.",
    "TSCO": "Tractor Supply Company",
    "TSEM": "Tower Semiconductor Ltd.",
    "TTEC": "TTEC Holdings Inc.",
    "TTGT": "TechTarget Inc.",
    "TTMI": "TTM Technologies Inc.",
    "TTOO": "T2 Biosystems Inc.",
    "TTWO": "Take-Two Interactive Software Inc.",
    "TUSK": "Mammoth Energy Services Inc.",
    "TVTX": "Travere Therapeutics Inc.",
    "TWIN": "Twin Disc Incorporated",
    "TWNK": "Hostess Brands Inc.",
    "TWOU": "2U Inc.",
    "TXMD": "TherapeuticsMD Inc.",
    "TXN": "Texas Instruments Incorporated",
    "TXRH": "Texas Roadhouse Inc.",
    "TYME": "Tyme Technologies Inc.",
    "UBCP": "United Bancorp Inc.",
    "UBFO": "United Security Bancshares",
    "UBSI": "United Bankshares Inc.",
    "UCBI": "United Community Banks Inc.",
    "UEIC": "Universal Electronics Inc.",
    "UEPS": "Net 1 UEPS Technologies Inc.",
    "UFCS": "United Fire Group Inc.",
    "UFPI": "UFP Industries Inc.",
    "UFPT": "UFP Technologies Inc.",
    "UG": "United-Guardian Inc.",
    "ULCC": "Frontier Group Holdings Inc.",
    "ULH": "Universal Logistics Holdings Inc.",
    "UMBF": "UMB Financial Corporation",
    "UMPQ": "Umpqua Holdings Corporation",
    "URGN": "UroGen Pharma Ltd.",
    "USAK": "USA Truck Inc.",
    "USAP": "Universal Stainless & Alloy Products Inc.",
    "USAT": "USA Technologies Inc.",
    "USAU": "U.S. Gold Corp.",
    "USEG": "U.S. Energy Corp.",
    "USIO": "Usio Inc.",
    "USLM": "United States Lime & Minerals Inc.",
    "USNA": "USANA Health Sciences Inc.",
    "USPH": "U.S. Physical Therapy Inc.",
    "UTHR": "United Therapeutics Corporation",
    "UTMD": "Utah Medical Products Inc.",
    "UTSI": "UTStarcom Holdings Corp.",
    "UVSP": "Univest Financial Corporation",
    "VABK": "Virginia National Bankshares Corporation",
    "VALU": "Value Line Inc.",
    "VBFC": "Village Bank and Trust Financial Corp.",
    "VBIV": "VBI Vaccines Inc.",
    "VBLT": "Vascular Biogenics Ltd.",
    "VBTX": "Veritex Holdings Inc.",
    "VCEL": "Vericel Corporation",
    "VCRA": "Vocera Communications Inc.",
    "VCTR": "Victory Capital Holdings Inc.",
    "VCYT": "Veracyte Inc.",
    "VEC": "Vectrus Inc.",
    "VIAP": "VIA optronics AG",
    "VIAV": "Viavi Solutions Inc.",
    "VICR": "Vicor Corporation",
    "VIEW": "View Inc.",
    "VIR": "Vir Biotechnology Inc.",
    "VIRC": "Virco Manufacturing Corporation",
    "VIRI": "Virios Therapeutics LLC",
    "VIRT": "Virtu Financial Inc.",
    "VISL": "Vislink Technologies Inc.",
    "WERN": "Werner Enterprises Inc.",
    "WETF": "WisdomTree Investments Inc.",
    "WEYS": "Weyco Group Inc.",
    "WHF": "WhiteHorse Finance Inc.",
    "WHLM": "Wilhelmina International Inc.",
    "WHLR": "Wheeler Real Estate Investment Trust Inc.",
    "WIFI": "Boingo Wireless Inc.",
    "WINA": "Winmark Corporation",
    "WING": "Wingstop Inc.",
    "WIRE": "Encore Wire Corporation",
    "WISA": "Summit Wireless Technologies Inc.",
    "WIX": "Wix.com Ltd.",
    "WKHS": "Workhorse Group Inc.",
    "WWE": "World Wrestling Entertainment Inc.",
    "WWR": "Westwater Resources Inc.",
    "WYNN": "Wynn Resorts Limited",
    "XAIR": "Beyond Air Inc.",
    "XBIT": "XBiotech Inc.",
    "XEL": "Xcel Energy Inc.",
    "XELA": "Exela Technologies Inc.",
    "XELB": "Xcel Brands Inc.",
    "XENE": "Xenon Pharmaceuticals Inc.",
    "XENT": "Intersect ENT Inc.",
    "XERS": "Xeris Pharmaceuticals Inc.",
    "XFOR": "X4 Pharmaceuticals Inc.",
    "XGN": "Exagen Inc.",
    "XLNX": "Xilinx Inc.",
    "ZNTL": "Zentalis Pharmaceuticals Inc.",
    "ZOM": "Zomedica Corp.",
    "ZS": "Zscaler Inc.",
    "ZYNE": "Zynerba Pharmaceuticals Inc.",
    "ZYXI": "Zynex Inc."
}

if __name__ == "__main__":
    print(f"Collecting financial data for {len(ticker_map)} companies ({YEARS[0]}-{YEARS[-1]})...")
    
    df = get_financial_data(ticker_map)
    
    if not df.empty:
    # Remove the debug column if needed
        df = df.drop(columns=['data_source'])
    
    # Save to Excel with desired formatting
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        # Format revenue column as plain numbers
            worksheet = writer.sheets['Sheet1']
            for row in worksheet.iter_rows(min_row=2, max_row=len(df)+1, min_col=5, max_col=5):
                for cell in row:
                    cell.number_format = '0'  
        
        print(f"\nSuccess! Collected data for {len(df['companyname'].unique())} companies")
        print(f"Saved to {OUTPUT_FILE}")
        
        print("\nSample data:")
        print(df.head())
    else:
        print("\nNo data was collected. Please check: Internet connection, Yahoo Finance API status, others")
       