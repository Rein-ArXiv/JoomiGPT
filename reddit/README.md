# Reddit Keyword Crawler Dataset

This repository contains a dataset of Reddit posts collected using the PRAW (Python Reddit API Wrapper) library.

## 🔍 Topic
This dataset focuses on Reddit posts that include the keyword: **"artificial intelligence"**

## 📅 Date of Crawling
2025-04-07

## 📄 Dataset Format

- File: `reddit_artificial_intelligence.json`
- Format: JSON
- Number of posts: 100

Each JSON object contains the following fields:

| Field         | Description                                      |
|---------------|--------------------------------------------------|
| `id`          | Reddit post ID                                   |
| `title`       | Title of the post                                |
| `selftext`    | Body of the post (may be empty)                  |
| `score`       | Number of upvotes                                |
| `url`         | URL of the original Reddit post                  |
| `subreddit`   | Subreddit name                                   |
| `created_utc` | Post creation time (ISO format, UTC)             |
| `num_comments`| Number of comments                               |
| `author`      | Reddit username of the author                    |

## 🧠 Intended Use

This dataset is designed for training or fine-tuning large language models (LLMs) on domain-specific or community-driven text data. It can be useful for:

- Text summarization
- Question answering
- Topic modeling
- Sentiment analysis
- Conversational agents

## ⚠️ Legal & Ethical Notice

- Use of this dataset should comply with Reddit's [API Terms of Use](https://www.redditinc.com/policies/data-api-terms)
- Do not use this dataset to target or harass individuals.
- Always respect user privacy when analyzing Reddit data.

## 🚀 How to Reproduce

Install dependencies:

```bash
pip install praw
