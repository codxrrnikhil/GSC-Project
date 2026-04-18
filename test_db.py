import requests


BASE_URL = "http://127.0.0.1:8000"


def main():
    print("Testing POST /test-db...")
    post_response = requests.post(f"{BASE_URL}/test-db", timeout=10)
    print(f"Status: {post_response.status_code}")
    print(f"Response: {post_response.text}")

    print("\nTesting GET /test-db...")
    get_response = requests.get(f"{BASE_URL}/test-db", timeout=10)
    print(f"Status: {get_response.status_code}")
    print(f"Response: {get_response.text}")


if __name__ == "__main__":
    main()
