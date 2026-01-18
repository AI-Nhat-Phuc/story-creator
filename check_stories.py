"""Quick script to check story content in database."""
from storage.nosql_storage import NoSQLStorage

s = NoSQLStorage('story_creator.db')
stories = s.stories.all()

print(f"Total stories: {len(stories)}")
print("=" * 60)

for i, story in enumerate(stories[:3], 1):
    print(f"\nStory {i}: {story['title']}")
    print(f"Content length: {len(story['content'])} characters")
    print(f"Content preview:\n{story['content'][:300]}...")
    print("-" * 60)
