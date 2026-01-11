"""i18n translation job examples."""

from translateplus import TranslatePlusClient
import time

client = TranslatePlusClient(api_key="your-api-key-here")

# Example 1: Create an i18n translation job
print("=== Example 1: Create i18n Job ===")

# Create a sample i18n file
sample_json = """{
    "welcome": "Welcome",
    "goodbye": "Goodbye",
    "thank_you": "Thank you"
}"""

with open("locales/en.json", "w") as f:
    f.write(sample_json)

# Create translation job
result = client.create_i18n_job(
    file_path="locales/en.json",
    target_languages=["fr", "es", "de"],
    source_language="en",
    webhook_url=None  # Optional webhook URL
)

job_id = result["job_id"]
print(f"Job created: {job_id}")
print(f"Status: {result.get('status', 'pending')}")
print()

# Example 2: Check job status
print("=== Example 2: Check Job Status ===")
status = client.get_i18n_job_status(job_id)
print(f"Job ID: {job_id}")
print(f"Status: {status['status']}")
print(f"Progress: {status.get('progress', 0)}%")
print(f"Source language: {status.get('source_language', 'N/A')}")
print(f"Target languages: {status.get('target_languages', [])}")
print()

# Example 3: Wait for job completion
print("=== Example 3: Wait for Completion ===")
max_wait = 300  # Maximum 5 minutes
wait_interval = 5  # Check every 5 seconds
elapsed = 0

while elapsed < max_wait:
    status = client.get_i18n_job_status(job_id)
    current_status = status["status"]
    
    print(f"Status: {current_status} (elapsed: {elapsed}s)")
    
    if current_status == "completed":
        print("Job completed!")
        break
    elif current_status == "failed":
        print(f"Job failed: {status.get('error', 'Unknown error')}")
        break
    
    time.sleep(wait_interval)
    elapsed += wait_interval
print()

# Example 4: Download translated files
if status.get("status") == "completed":
    print("=== Example 4: Download Translated Files ===")
    target_languages = status.get("target_languages", [])
    
    for lang in target_languages:
        try:
            content = client.download_i18n_file(job_id, lang)
            output_path = f"locales/{lang}.json"
            with open(output_path, "wb") as f:
                f.write(content)
            print(f"Downloaded: {output_path}")
        except Exception as e:
            print(f"Error downloading {lang}: {e}")
    print()

# Example 5: List all jobs
print("=== Example 5: List All Jobs ===")
jobs = client.list_i18n_jobs(page=1, page_size=10)
print(f"Total jobs: {jobs.get('count', 0)}")
print(f"Page: {jobs.get('page', 1)}")
print(f"Page size: {jobs.get('page_size', 20)}")
print()

for job in jobs.get("results", []):
    print(f"Job {job['id']}: {job['status']} - {job.get('source_language', 'N/A')} -> {job.get('target_languages', [])}")
print()

# Example 6: Delete job (optional)
print("=== Example 6: Delete Job ===")
# Uncomment to delete the job
# client.delete_i18n_job(job_id)
# print(f"Job {job_id} deleted")
print()

client.close()
