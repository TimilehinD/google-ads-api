from google.cloud import secretmanager
from google.cloud import bigquery
from google.ads.googleads.client import GoogleAdsClient

# Function to retrieve secret from Secret Manager
def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode("UTF-8")

# Set the Google Cloud project ID and Secret ID
project_id = "glancehair-1691487293868"
secret_id = "my_api_secret"

# Retrieve service account key from Secret Manager
service_account_key_json = get_secret(project_id, secret_id)

# Initialize BigQuery client using service account key
bigquery_client = bigquery.Client.from_service_account_info(service_account_key_json)

# Initialize Google Ads client using service account key
google_ads_client = GoogleAdsClient.load_from_storage(service_account_key_json)

# The rest of your code remains unchanged...

# Make API requests using the Google Ads client
customer_id = '214-846-1507'
query = """
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad.id,
      ad.type,
      ad.headline,
      ad.description,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      impressions,
      clicks,
      conversions,
      cost_micros
    FROM
      ad
"""
response = google_ads_client.service.google_ads.search(query=query, customer_id=customer_id)

# Process the response and send data to BigQuery
dataset_id = 'glancehair-1691487293868.stadly'
table_id = 'glancehair-1691487293868.stadly.google ads'

# Create BigQuery dataset if not exists
dataset_ref = bigquery_client.dataset(dataset_id)
dataset = bigquery.Dataset(dataset_ref)
bigquery_client.create_dataset(dataset, exists_ok=True)

# Create or get the BigQuery table
table_ref = bigquery_client.dataset(dataset_id).table(table_id)
table = bigquery_client.get_table(table_ref)

# Insert rows into the BigQuery table
rows_to_insert = []
for row in response:
    campaign_id = row.campaign.id.value if row.campaign.id else None
    campaign_name = row.campaign.name.value if row.campaign.name else None
    ad_group_id = row.ad_group.id.value if row.ad_group.id else None
    ad_group_name = row.ad_group.name.value if row.ad_group.name else None
    ad_id = row.ad.id.value if row.ad.id else None
    ad_type = row.ad.type if row.ad.type else None
    headline = row.ad.headline.value if row.ad.headline else None
    description = row.ad.description.value if row.ad.description else None
    impressions = row.impressions.value if row.impressions else None
    clicks =  row.clicks.value if row.clicks else None
    conversions =  row.conversions.value if row.conversions else None
    cost_micros = row.cost_micros.value if row.cost_micros else None
    keyword_criterion_id = row.ad_group_criterion.criterion_id.value if row.ad_group_criterion.criterion_id else None
    keyword_text = row.ad_group_criterion.keyword.text.value if row.ad_group_criterion.keyword and row.ad_group_criterion.keyword.text else None

    rows_to_insert.append((
        campaign_id,
        campaign_name,
        ad_group_id,
        ad_group_name,
        ad_id,
        ad_type,
        headline,
        description,
        keyword_criterion_id,
        keyword_text,
        impressions,
        clicks,
        conversions,
        cost_micros
    ))

# Use the BigQuery client to insert rows
bigquery_client.insert_rows(table, rows_to_insert)

# Print the processed response
for row in response:
    print(row)
