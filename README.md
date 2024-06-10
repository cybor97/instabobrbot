# InstaBobrBot

InstaBobrBot is a Telegram bot that downloads Instagram reels and sends them directly to your Telegram channel.

## Setup

1. Clone the repository:
```sh
git clone https://github.com/cybor97/instabobrbot
cd instabobrbot
```

2. Create a virtual environment and activate it:
```sh
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```sh
pip install -r requirements.txt
```

4. Set up the environment variables in the Env Secrets tab:
  - `TELEGRAM_API_TOKEN`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION`
  - `S3_ENDPOINT_URL`
  - `S3_BUCKET_NAME`

5. Run the bot:
  ```sh
  python main.py
  ```

## Docker Setup

1. Build the Docker image:
```sh
docker build -t instabobrbot .
```

2. Run the Docker container:
```sh
docker-compose up
```