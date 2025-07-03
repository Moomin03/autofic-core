# Copyright 2025 Autofic Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""Contains their functional aliases.
"""
import os
import subprocess
import click

# Handles creation and git operations for GitHub Actions workflow YAML files
class AboutYml:
    """
    Class for managing GitHub Actions workflow YAML files.
    Provides methods to create workflow files and push them to a repository.
    """
    def __init__(self, start_dir="."):
        """
        Initialize with the starting directory (default: current directory).
        :param start_dir: Base directory for workflow file operations.
        """
        self.start_dir = start_dir
        
    def create_pr_yml(self):
        """
        Create the 'pr_notify.yml' GitHub Actions workflow file.
        This workflow sends notifications to Discord and Slack when a pull request is opened, reopened, or closed.
        """
        workflow_dir = os.path.join(self.start_dir, ".github", "workflows")
        os.makedirs(workflow_dir, exist_ok=True)

        pr_notify_yml_path = os.path.join(workflow_dir, "pr_notify.yml")
        pr_notify_yml_content = """name: Autofic SAST for Selected JavaScript Repos

on:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: '00 21 * * 0'  # 매주 월요일 오전 6시

jobs:
  eslint-check:
    name: ESLint Check
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install Node dependencies
        run: |
          if [ -f package-lock.json ]; then
            npm ci
          else
            npm install
          fi

      - name: Run ESLint check
        run: npx eslint . --ext .js,.jsx

  find-and-run:
    name: Python SAST Runner
    runs-on: ubuntu-latest
    needs: eslint-check  # ✅ ESLint 성공해야 실행됨 (선택)

    steps:
      - name: Checkout this repository
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -e .

      - name: Set Git config
        run: |
          git config --global user.email "github-actions@users.noreply.github.com"
          git config --global user.name "github-actions"

      - name: Run ci_automation.py automatically
        env:
          GITHUB_TOKEN: ${{ secrets.GIT_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPEN_API_KEY }}
          USER_NAME: ${{ secrets.USER_NAME }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          python src/autofic_core/ci_cd_auto/ci_automation.py
"""
        with open(pr_notify_yml_path, "w", encoding="utf-8") as f:
            f.write(pr_notify_yml_content)
            
    def create_eslint_yml(self):
      
            
    def push_pr_yml(self, user_name, repo_name, token, branch_name):
        """
        Adds, commits, and pushes the created workflow YAML file to the specified git branch.
        The remote URL is set to use the provided GitHub token for authentication. (Needed!)

        :param user_name: GitHub username (repository owner)
        :param repo_name: Name of the repository
        :param token: GitHub access token (for authentication)
        :param branch_name: Name of the branch to push to
        """
        repo_url = f'https://x-access-token:{token}@github.com/{user_name}/{repo_name}.git'
        subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url], check=True)
        click.secho("[ INFO ] Pushing the generated .github/workflows/pr_notify.yml.", fg="yellow")
        subprocess.run(['git', 'add', '.github/workflows/pr_notify.yml'], check=True)
        subprocess.run(['git', 'commit', '-m', "[Autofic] Create package.json and CI workflow"], check=True)
        subprocess.run(['git', 'push', 'origin', branch_name], check=True)
