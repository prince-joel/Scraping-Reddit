import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

scraper_api_key = 'cbc003ea3b6967aaf68087cbf9cc51c1'

def fetch_reddit_cookies():
    r = requests.get("https://reddit.com/")
    return r.cookies.get_dict()

def fetch_posts_from_query(query):
    reddit_query = f"https://www.reddit.com/search/?q={query}"
    scraper_api_url = f'http://api.scraperapi.com/?api_key={scraper_api_key}&url={reddit_query}'
    r = requests.get(scraper_api_url)
    reddit_query_page = BeautifulSoup(r.content, "html.parser")
    
    posts = reddit_query_page.find_all("faceplate-tracker", {"action": "view"})
    parsed_posts = list()
    for index, post in enumerate(posts, start=1):
        post_data = json.loads(post["data-faceplate-tracking-context"])
        

        if "post" in post_data:
            image_data = reddit_query_page.find("faceplate-img", {"alt": post_data["post"]["title"]})
            image_src = ''
            if image_data:
                image_src = image_data["src"]
            parsed_posts.append({
                "index": index,
                "title": post_data["post"]["title"],
                "created_datetime": datetime.fromtimestamp(post_data["post"]["created_timestamp"] / 1000),
                "url": post_data["post"]["url"],
                "post_id": post_data["post"]["id"],
                "subreddit_name": post_data["post"]["subreddit_name"],
                "subreddit_id": post_data["post"]["subreddit_id"],
                "image_src": image_src
            })
            print(f"{index}. Title:{post_data['post']['title']} Url:{post_data['post']['url']} image: {image_src}")
    return parsed_posts

def fetch_comments_from_post(post_data, cookies):
    reddit_comments_url = f"https://www.reddit.com/svc/shreddit/more-comments/{post_data['subreddit_name']}/{post_data['post_id']}?top-level=1"
    r = requests.post(reddit_comments_url, cookies=cookies)
    reddit_comments_page = BeautifulSoup(r.content, "html.parser")
    
    comments = reddit_comments_page.find_all("shreddit-comment", {"postid": post_data["post_id"]})
    parsed_comments = list()
    try: 
        for comment in comments:
            parsed_comments.append({
                "author": comment["author"],
                "permalink": comment["permalink"],
                "text": comment.find("p").text.strip()
            })
    except:
        print("No comments for this post.")
        
        
    return parsed_comments

if __name__ == "__main__":
    # Prompt the user for the query
    search_query = input("Enter the Reddit search query: ")
    
    # Fetch all posts from the provided query
    posts = fetch_posts_from_query(search_query)
    cookies = fetch_reddit_cookies()

    # Prompt the user to pick a post
    selected_post_index = int(input("Enter the number of the post you want to view comments for: "))
    
    # Validate the user's input
    if 1 <= selected_post_index <= len(posts):
        selected_post = posts[selected_post_index - 1]
        comments = fetch_comments_from_post(selected_post, cookies)

        # Print the comments of the selected post
        for comment in comments:
            print(comment, end="\n\n")
    else:
        print("Invalid post number. Please enter a valid number.")