import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'listings.db')
DEBUG_DIR = os.path.join(BASE_DIR, 'data', 'debug')

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

TARGET_REGIONS = {
    'singapore', 'malaysia', 'thailand', 'indonesia', 'philippines',
    'vietnam', 'hong kong', 'taiwan', 'myanmar', 'cambodia', 'laos',
    'brunei', 'asia', 'southeast asia', 'asean', 'apac',
}

TARGET_INDUSTRIES = {
    'professional services', 'accounting', 'legal', 'law firm', 'consulting',
    'marketing agency', 'agency', 'financial services', 'insurance', 'staffing',
    'manufacturing', 'distribution', 'wholesale', 'logistics', 'supply chain',
    'restaurant', 'food & beverage', 'cafe', 'bakery',
    'retail', 'shop', 'laundry', 'cleaning', 'automotive', 'auto',
    'healthcare', 'clinic', 'beauty', 'salon', 'spa',
    'education', 'childcare', 'fitness', 'gym',
}

SOURCES = [
    {
        'id': 'bizbuysell',
        'name': 'BizBuySell',
        'url': 'https://www.bizbuysell.com',
        'color': '#0d6efd',
        'description': 'Major US marketplace with international listings',
    },
    {
        'id': 'businessesforsale',
        'name': 'BusinessesForSale.com',
        'url': 'https://www.businessesforsale.com',
        'color': '#198754',
        'description': 'Global marketplace with dedicated Singapore/Asia sections',
    },
    {
        'id': 'matchasia',
        'name': 'match.asia',
        'url': 'https://www.match.asia',
        'color': '#fd7e14',
        'description': 'Singapore & SE Asia focused business marketplace',
    },
    {
        'id': 'acquire',
        'name': 'Acquire.com',
        'url': 'https://acquire.com',
        'color': '#6f42c1',
        'description': 'Online & SaaS businesses for sale globally',
    },
]

SOURCE_MAP = {s['id']: s for s in SOURCES}
