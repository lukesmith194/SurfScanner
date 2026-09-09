"""Seeds a test account plus a couple of others so the Community page has
something to look at immediately instead of empty states everywhere.

Run once with: .venv/bin/python seed_demo_data.py
"""

import datetime

import auth
import social
from db import init_db

TEST_EMAIL = "test@surfscanner.com"
TEST_PASSWORD = "surftest123"

if __name__ == "__main__":
    init_db()

    test_user = auth.sign_up(TEST_EMAIL, TEST_PASSWORD, "Test Surfer", "Dublin", "Intermediate")
    alex = auth.sign_up("alex@surfscanner.com", "password123", "Alex", "London", "Advanced")
    sarah = auth.sign_up("sarah@surfscanner.com", "password123", "Sarah", "Lisbon", "Beginner")

    if not (test_user.ok and alex.ok and sarah.ok):
        print("Some accounts already existed — skipping re-seed. Delete surfscanner.db to start fresh.")
    else:
        today = datetime.date.today()

        # Test Surfer follows Alex and posts their own trip.
        social.follow(test_user.user_id, alex.user_id)
        social.create_post(
            test_user.user_id, "Bundoran", today + datetime.timedelta(days=20),
            today + datetime.timedelta(days=27), "Intermediate", "Who's up for this one?",
        )

        # Alex (followed) posts a trip, Sarah (not followed) posts one too.
        social.create_post(
            alex.user_id, "Fistral Beach", today + datetime.timedelta(days=10),
            today + datetime.timedelta(days=13), "Advanced", "Big swell forecast, heading down.",
        )
        social.create_post(
            sarah.user_id, "Zarautz", today + datetime.timedelta(days=30),
            today + datetime.timedelta(days=35), "Beginner", "",
        )

        # A comment and an interest, so those UI states aren't empty either.
        alex_post = social.feed_for(test_user.user_id)[0]  # newest-first: Alex's post
        social.add_comment(alex_post.post_id, test_user.user_id, "Wish I could make this one!")
        social.toggle_interest(alex_post.post_id, test_user.user_id)

        print("Seeded 3 accounts, 3 posts, 1 comment, 1 interest.")

    print(f"\nLog in as: {TEST_EMAIL} / {TEST_PASSWORD}")
