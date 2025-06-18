"""
Debug script to check agent messages in the database
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Set up Django-style imports for the frontend DB
os.environ.setdefault('DATABASE_URL', 'postgres://localhost/ai_hedge_fund')

# Import SQLite directly to check the frontend database
import sqlite3
import json

# Path to the frontend database
db_path = Path(__file__).parent / "app" / "frontend" / ".next" / "dev.db"

if not db_path.exists():
    print(f"❌ Database not found at: {db_path}")
    # Try alternative paths
    alt_paths = [
        Path(__file__).parent / "app" / "frontend" / "dev.db",
        Path(__file__).parent / "app" / "frontend" / "local.db",
        Path(__file__).parent / "app" / "frontend" / ".db",
    ]
    for alt_path in alt_paths:
        if alt_path.exists():
            db_path = alt_path
            print(f"✅ Found database at: {db_path}")
            break
    else:
        print("❌ Could not find any database file")
        sys.exit(1)

print(f"📊 Checking database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get the most recent messages
query = """
SELECT m.id, m.chatId, m.role, m.parts, m.attachments, m.createdAt, c.agentType
FROM Message m
LEFT JOIN Chat c ON m.chatId = c.id
ORDER BY m.createdAt DESC
LIMIT 10
"""

try:
    cursor.execute(query)
    messages = cursor.fetchall()
    
    print(f"\n📬 Found {len(messages)} recent messages:")
    print("-" * 80)
    
    for msg in messages:
        msg_id, chat_id, role, parts_json, attachments_json, created_at, agent_type = msg
        
        print(f"\n🔍 Message ID: {msg_id[:8]}...")
        print(f"   Chat ID: {chat_id[:8]}...")
        print(f"   Role: {role}")
        print(f"   Agent Type: {agent_type or 'general'}")
        print(f"   Created: {created_at}")
        
        # Parse parts
        try:
            parts = json.loads(parts_json) if parts_json else []
            print(f"   Parts: {len(parts)}")
            
            for i, part in enumerate(parts):
                part_type = part.get('type', 'unknown')
                print(f"   - Part {i}: type={part_type}")
                
                if part_type == 'text':
                    text = part.get('text', '')
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"     Text: {preview}")
                elif part_type == 'tool-invocation':
                    tool_inv = part.get('toolInvocation', {})
                    print(f"     Tool: {tool_inv.get('toolName', 'unknown')}")
                    print(f"     State: {tool_inv.get('state', 'unknown')}")
                    
        except json.JSONDecodeError as e:
            print(f"   ❌ Error parsing parts: {e}")
            print(f"   Raw parts: {parts_json[:200]}...")
            
        print("-" * 40)
        
except Exception as e:
    print(f"\n❌ Error querying database: {e}")
    # Try to list tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📋 Available tables: {[t[0] for t in tables]}")

finally:
    conn.close()

print("\n✅ Debug complete") 