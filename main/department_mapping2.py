from transformers import pipeline
import json, os, time

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=0
)

DEPARTMENTS = [
    "Security",
    "Engineering",
    "IT",
    "Data",
    "Sales",
    "Marketing",
    "HR",
    "Finance",
    "Operations"
]


CACHE_FILE = "department_cache.json"


def call_local_ai_batch(batch_dict):
    """
    Local zero-shot department mapping.
    Input:  { "Job Title": "" }
    Output: { "Job Title": "Department" }
    """
    results = {}

    for title in batch_dict:
        try:
            prediction = classifier(title, DEPARTMENTS)
            results[title] = prediction["labels"][0]
        except Exception as e:
            results[title] = "Unknown"

    return results


def process_people_safely(prospects):

    people  = prospects["data"]

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    missing_positions = list({
        p["position"].strip()
        for p in people
        if p.get("position")
        and p["position"].strip().lower() not in cache
    })
    BATCH_SIZE = 5

    if missing_positions:
        total_batches = (len(missing_positions) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(missing_positions), BATCH_SIZE):
            chunk = missing_positions[i : i + BATCH_SIZE]
            lookup = {pos: "" for pos in chunk}


            results = call_local_ai_batch(lookup)

            for pos, dept in results.items():
                cache[pos.lower()] = dept

            with open(CACHE_FILE, "w") as f:
                json.dump(cache, f, indent=4)

            time.sleep(1)

    for person in people:
        pos_key = person.get("position", "").strip().lower()
        person["department"] = cache.get(pos_key, "Unknown")

    return people


