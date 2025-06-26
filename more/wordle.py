import datetime
import requests

def get_url(date: datetime.date) -> str:
    return f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"

def main():
    date = datetime.date.today()
    response = requests.get(get_url(date)).json()
    print(f"Today's Wordle answer: {response['solution']}")

if __name__ == "__main__":
    main()