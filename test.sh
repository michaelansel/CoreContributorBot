source .env
docker run -it --rm -e "GITHUB_TOKEN=$GITHUB_TOKEN" -e "OPENAI_API_KEY=$OPENAI_API_KEY" -e "GH_REPO=$GH_REPO" github-bot python bot.py test