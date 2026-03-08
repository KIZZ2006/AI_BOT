import requests
import json

OPENROUTER_API_KEY = "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"

def get_free_models():
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json().get('data', [])
        free_models = []
        for m in models:
            # Check if pricing is 0
            pricing = m.get('pricing', {})
            prompt = float(pricing.get('prompt', 0))
            completion = float(pricing.get('completion', 0))
            if prompt == 0 and completion == 0:
                free_models.append(m['id'])
        return free_models
    else:
        print(f"Error: {response.status_code}")
        return []

if __name__ == "__main__":
    free_list = get_free_models()
    print("🆓 CURRENT FREE MODELS ON OPENROUTER:")
    for m in sorted(free_list):
        print(f" - {m}")
