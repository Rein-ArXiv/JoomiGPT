import praw
import json
from datetime import datetime

# Reddit API 인증
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="KeywordCrawler/0.1 by YOUR_USERNAME"
)

# 설정
keyword = "artificial intelligence"
subreddit_name = "all"
limit = 100

# 크롤링 실행
data = []
for submission in reddit.subreddit(subreddit_name).search(keyword, sort='new', limit=limit):
    post = {
        "id": submission.id,
        "title": submission.title,
        "selftext": submission.selftext,
        "score": submission.score,
        "url": submission.url,
        "subreddit": str(submission.subreddit),
        "created_utc": datetime.utcfromtimestamp(submission.created_utc).isoformat() + "Z",
        "num_comments": submission.num_comments,
        "author": str(submission.author)
    }
    data.append(post)

# JSON 저장
with open(f"reddit_{keyword.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"{len(data)}개의 게시글이 저장되었습니다.")
