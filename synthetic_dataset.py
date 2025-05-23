import pandas as pd
import random
from faker import Faker
import datetime

# Initialize Faker for realistic data
fake = Faker()

# Define constants
NUM_ROWS = 50000
CONTINENTS = {
    'North America': ['USA', 'Canada', 'Mexico'],
    'Europe': ['UK', 'Germany', 'France', 'Italy', 'Spain'],
    'Asia': ['Japan', 'China', 'India', 'UAE', 'South Korea'],
    'Africa': ['South Africa', 'Nigeria', 'Kenya', 'Egypt', 'Ghana', 'Ethiopia', 'Algeria', 'Uganda', 'Morocco', 'Tanzania'],
    'South America': ['Brazil', 'Argentina'],
    'Oceania': ['Australia', 'New Zealand']
}
DISTRIBUTION = {'North America': 0.35, 'Europe': 0.25, 'Asia': 0.20, 'Africa': 0.10, 'South America': 0.05, 'Oceania': 0.05}
SALESPEOPLE = ['SP001', 'SP002', 'SP003', 'SP004', 'SP005', 'SP006']
PRODUCT_TYPES = ['AI-Powered CRM', 'Virtual Assistant Suite', 'Predictive Analytics Platform', 'Automated Workflow Engine']
REQUEST_TYPES = ['demo', 'ai_assist', 'promo', 'job']
JOB_TYPES = ['software_dev', 'prototyping', 'consulting']
STATUS_CODES = [200, 404]
AFFILIATE_CODES = [fake.bothify(text='AF###') for _ in range(100)]
START_DATE = datetime.datetime(2024, 1, 1)
END_DATE = datetime.datetime(2025, 5, 31)

# Generate data
data = []
for _ in range(NUM_ROWS):
    # Select continent and country based on distribution
    continent = random.choices(list(DISTRIBUTION.keys()), weights=DISTRIBUTION.values())[0]
    country = random.choice(CONTINENTS[continent])
    
    # Timestamp with varied time
    days = (END_DATE - START_DATE).days
    random_date = START_DATE + datetime.timedelta(days=random.randint(0, days))
    random_time = datetime.time(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )
    timestamp = datetime.datetime.combine(random_date, random_time).strftime('%Y-%m-%d %H:%M:%S')
    
    # Salesperson (region-specific bias)
    salesperson = random.choice(SALESPEOPLE)
    
    # Product type
    product_type = random.choice(PRODUCT_TYPES)
    
    # Request type and job type (if applicable)
    request_type = random.choice(REQUEST_TYPES)
    job_type = random.choice(JOB_TYPES) if request_type == 'job' else ''
    
    # Status code
    status_code = random.choice(STATUS_CODES)
    
    # Affiliate code
    affiliate_code = random.choice(AFFILIATE_CODES)
    
    # Revenue and purchase flag
    revenue = round(random.uniform(100, 300), 2) if request_type in ['job', 'demo'] and random.random() < 0.3 else 0.00
    purchase_flag = 1 if revenue > 0 and random.random() < 0.5 else 0
    
    data.append([timestamp, country, continent, salesperson, product_type, request_type, job_type, status_code, affiliate_code, revenue, purchase_flag])

# Create DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'country', 'continent', 'salesperson_id', 'product_type', 'request_type', 'job_type', 'status_code', 'affiliate_code', 'revenue ($)', 'purchase_flag'])

# Save to CSV
df.to_csv('al_solutions_sales_data.csv', index=False)

print("Dataset generated and saved as 'al_solutions_sales_data.csv' with 50,000 rows.")