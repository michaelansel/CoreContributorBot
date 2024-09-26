# GitHub Bot

This repository contains a GitHub bot that automatically processes issues and pull requests using an AI-powered RAG loop. The bot is implemented in Python and runs in a Docker container.

## Features

- Monitors new issues and generates code changes using a RAG loop
- Creates pull requests with the generated code changes
- Processes pull request comments and updates the pull request with additional code changes

## Requirements

- Python 3.9
- Docker
- GitHub API token
- OpenAI API key

## Setup

1. Clone the repository
2. Create a `.env` file based on the `.env.sample` file and add your GitHub and OpenAI API tokens
3. Build the Docker image by running `./build.sh`
4. Run the unit tests by running `./test.sh`
5. Run the bot by running `./run.sh`

## Automated Testing

The repository includes a GitHub Actions workflow that automatically runs the build and test scripts on every pull request. The workflow is defined in the `.github/workflows/test.yml` file.

Pull requests can only be merged if the automated tests pass successfully.