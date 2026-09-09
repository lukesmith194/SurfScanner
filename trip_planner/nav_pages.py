"""Shared references to this app's st.Page objects, set once by main.py
right after creating them. Needed because pages defined from callables
(as all of this app's are, rather than script files) are only targetable
by st.page_link/st.switch_page via the actual Page object — a string path
doesn't resolve for them — so other modules need a way to reach the same
objects main.py created.
"""

home_page = None
account_page = None
trip_planner_page = None
community_page = None
