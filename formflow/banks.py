"""Python port of includes/banks.php."""


def formflow_banks():
    banks = [
        {"id": "sbi", "bank_name": "State Bank of India", "short_name": "SBI", "url": "https://sbi.co.in/", "source": "State Bank of India Official Website"},
        {"id": "hdfc", "bank_name": "HDFC Bank", "short_name": "HDFC", "url": "https://www.hdfcbank.com/", "source": "HDFC Bank Official Website"},
        {"id": "icici", "bank_name": "ICICI Bank", "short_name": "ICICI", "url": "https://www.icicibank.com/", "source": "ICICI Bank Official Website"},
        {"id": "axis", "bank_name": "Axis Bank", "short_name": "Axis", "url": "https://www.axisbank.com/", "source": "Axis Bank Official Website"},
        {"id": "idfc_first", "bank_name": "IDFC FIRST Bank", "short_name": "IDFC FIRST", "url": "https://www.idfcfirstbank.com/", "source": "IDFC FIRST Bank Official Website"},
        {"id": "kotak", "bank_name": "Kotak Mahindra Bank", "short_name": "Kotak", "url": "https://www.kotak.com/", "source": "Kotak Mahindra Bank Official Website"},
        {"id": "indian_bank", "bank_name": "Indian Bank", "short_name": "Indian Bank", "url": "https://www.indianbank.in/", "source": "Indian Bank Official Website"},
        {"id": "canara", "bank_name": "Canara Bank", "short_name": "Canara", "url": "https://canarabank.com/", "source": "Canara Bank Official Website"},
        {"id": "bank_of_baroda", "bank_name": "Bank of Baroda", "short_name": "BoB", "url": "https://www.bankofbaroda.in/", "source": "Bank of Baroda Official Website"},
        {"id": "union", "bank_name": "Union Bank of India", "short_name": "Union Bank", "url": "https://www.unionbankofindia.co.in/", "source": "Union Bank of India Official Website"},
        {"id": "bank_of_india", "bank_name": "Bank of India", "short_name": "BOI", "url": "https://bankofindia.co.in/", "source": "Bank of India Official Website"},
        {"id": "indian_overseas", "bank_name": "Indian Overseas Bank", "short_name": "IOB", "url": "https://www.iob.in/", "source": "Indian Overseas Bank Official Website"},
        {"id": "pnb", "bank_name": "Punjab National Bank", "short_name": "PNB", "url": "https://www.pnbindia.in/", "source": "Punjab National Bank Official Website"},
        {"id": "central_bank", "bank_name": "Central Bank of India", "short_name": "Central Bank", "url": "https://www.centralbankofindia.co.in/", "source": "Central Bank of India Official Website"},
        {"id": "bank_of_maharashtra", "bank_name": "Bank of Maharashtra", "short_name": "Bank of Maharashtra", "url": "https://bankofmaharashtra.in/", "source": "Bank of Maharashtra Official Website"},
        {"id": "uco", "bank_name": "UCO Bank", "short_name": "UCO", "url": "https://www.ucobank.com/", "source": "UCO Bank Official Website"},
        {"id": "punjab_sind", "bank_name": "Punjab & Sind Bank", "short_name": "Punjab & Sind", "url": "https://punjabandsindbank.co.in/", "source": "Punjab & Sind Bank Official Website"},
        {"id": "idbi", "bank_name": "IDBI Bank", "short_name": "IDBI", "url": "https://www.idbibank.in/", "source": "IDBI Bank Official Website"},
        {"id": "federal", "bank_name": "Federal Bank", "short_name": "Federal", "url": "https://www.federalbank.co.in/", "source": "Federal Bank Official Website"},
        {"id": "south_indian", "bank_name": "South Indian Bank", "short_name": "South Indian Bank", "url": "https://www.southindianbank.com/", "source": "South Indian Bank Official Website"},
        {"id": "kvb", "bank_name": "Karur Vysya Bank", "short_name": "KVB", "url": "https://www.kvb.co.in/", "source": "Karur Vysya Bank Official Website"},
        {"id": "city_union", "bank_name": "City Union Bank", "short_name": "CUB", "url": "https://www.cityunionbank.com/", "source": "City Union Bank Official Website"},
        {"id": "tmb", "bank_name": "Tamilnad Mercantile Bank", "short_name": "TMB", "url": "https://www.tmbnet.in/", "source": "Tamilnad Mercantile Bank Official Website"},
        {"id": "rbl", "bank_name": "RBL Bank", "short_name": "RBL", "url": "https://www.rblbank.com/", "source": "RBL Bank Official Website"},
        {"id": "indusind", "bank_name": "IndusInd Bank", "short_name": "IndusInd", "url": "https://www.indusind.com/", "source": "IndusInd Bank Official Website"},
    ]
    result = {"other": {"id": "other", "bank_name": "Other Bank", "short_name": "Other Bank", "url": None, "source": "FormFlow verified bank directory", "verified": False}}
    for bank in banks:
        bank = dict(bank)
        bank["verified"] = True
        result[bank["id"]] = bank
    return result


def formflow_kyc_purposes():
    return {
        "new_account": "New Account / KYC",
        "update": "Update KYC / Re-KYC",
        "guidelines": "KYC Guidelines",
        "documents": "KYC Form / Documents",
        "unsure": "I'm not sure",
    }
