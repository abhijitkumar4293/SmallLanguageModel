"""
Enhanced Reddit API client with hierarchical comment extraction.
Based on user's provided RedditApiClient class.
"""

import os
import json
import praw
import datetime
from typing import Dict, List, Any


class RedditApiClient:
    """Client to hit reddit API, necessary for fetching reddit posts and info."""

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        user_agent=None,
    ) -> None:
        self._reddit_client = self._init_reddit_client(
            client_id, client_secret, user_agent
        )

    def _init_reddit_client(self, client_id, client_secret, user_agent):
        if client_id and client_secret and user_agent:
            return praw.Reddit(
                client_id=client_id, client_secret=client_secret, user_agent=user_agent
            )
        else:
            raise ValueError(f"Reddit credentials are not appropriately defined")

    def search_for_subreddits_api(self, query, limit=15):
        """Search for subreddits matching query."""
        subreddits = self._reddit_client.subreddits.search(query, limit=limit)
        result_list = [subreddit.display_name for subreddit in subreddits]
        return result_list

    def fetch_comments_subreddit_api(
        self, query, subreddit_name, limit=10, sort="relevance", time_filter="month"
    ):
        """Fetch posts from subreddit matching query."""
        subreddit = self._reddit_client.subreddit(subreddit_name)
        result_list = subreddit.search(
            query, limit=limit, sort=sort, time_filter=time_filter
        )
        return result_list

    def extract_post_and_comments(self, post_id) -> Dict[str, Any]:
        """
        Extract post and all comments hierarchically.

        Returns dict with:
        - title, author, body, url
        - number_of_comments, score, upvote_ratio
        - comments (hierarchical list)
        """
        def extract_comments_hierarchically(comments):
            """Recursively extract comments and their replies."""
            comments_list = []
            for comment in comments:
                # Check if the comment is a MoreComments object
                if isinstance(comment, praw.models.MoreComments):
                    # If it is, skip it
                    continue
                comment_data = {
                    "author": comment.author.name if comment.author else "[deleted]",
                    "body": comment.body,
                    "replies": extract_comments_hierarchically(comment.replies),
                }
                comments_list.append(comment_data)
            return comments_list

        def get_post_awards(submission):
            """Extract awards from submission."""
            awards = []
            for award in submission.all_awardings:
                awards.append({"name": award["name"], "count": award["count"]})
            return awards

        try:
            submission = self._reddit_client.submission(id=post_id)
            post_data = {
                "title": submission.title,
                "author": submission.author.name if submission.author else "[deleted]",
                "body": submission.selftext,
                "url": submission.url,
                "number_of_comments": submission.num_comments,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "awards": get_post_awards(submission),
                "comments": extract_comments_hierarchically(submission.comments),
                "created_utc": datetime.datetime.fromtimestamp(
                    submission.created_utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
            }
            return post_data
        except Exception as e:
            # If an exception is raised, the post ID is invalid
            print(f"An unexpected error occurred: {e}")
            return {}

    def get_subreddit_top_posts(
        self,
        subreddit_name: str,
        limit: int = 100,
        time_filter: str = "month"
    ) -> List:
        """
        Get top posts from a subreddit.

        Args:
            subreddit_name: Name of subreddit (without r/)
            limit: Number of posts to fetch
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'

        Returns:
            List of submission objects
        """
        subreddit = self._reddit_client.subreddit(subreddit_name)
        return list(subreddit.top(time_filter=time_filter, limit=limit))
