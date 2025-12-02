# 🚀 Quick Reference Card

## Database Setup (Do This First!)

### 1. Create Tables (2 min)
Go to: https://supabase.com/dashboard/project/pozqlghiwukecwtuhbjh/sql/new

Run this SQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  price NUMERIC NOT NULL,
  stock_quantity INT NOT NULL DEFAULT 0,
  category TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT,
  metadata JSONB,
  embedding VECTOR(384)
);

CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (id UUID, content TEXT, metadata JSONB, similarity FLOAT)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT documents.id, documents.content, documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END; $$;
```

### 2. Load Data (2 min)
```bash
cd /home/mamunhossain/Projects/recipe/recipe_AI_Multi_Agent_System
source venv/bin/activate
python backend/scripts/setup_complete_system.py
```

---

## Start/Stop Server

### Start Backend
```bash
cd /home/mamunhossain/Projects/recipe/recipe_AI_Multi_Agent_System
source venv/bin/activate
python -m uvicorn backend.main:app --reload --port 8000
```

### Stop Backend
```bash
pkill -f uvicorn
```

### Check Status
```bash
curl http://localhost:8000/health
```

---

## Test Commands

### Recipe Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have chicken and rice. What can I cook?"}'
```

### Product Search
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me available meat options"}'
```

### Support Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your return policy?"}'
```

---

## Customer Query Examples

### 👨‍🍳 Recipes
- "I have chicken and rice, what can I cook?"
- "Show me fish recipes"
- "How to make tehari?"
- "Dessert suggestions"

### 🛍️ Products
- "Show me available meat options"
- "What vegetables do you have?"
- "How much does chicken cost?"
- "Is beef available?"

### 📞 Support
- "What is your return policy?"
- "How do I get a refund?"
- "Delivery charges?"
- "Contact support?"

---

## File Locations

### Backend
- Main: `backend/main.py`
- Agents: `backend/agents/*.py`
- Tools: `backend/tools/*.py`
- Data: `backend/data/*.json`

### Setup Scripts
- Complete setup: `backend/scripts/setup_complete_system.py`
- Seed data: `backend/scripts/seed_data.py`

### Documentation
- Quick setup: `QUICK_SETUP_GUIDE.md`
- Full testing: `FINAL_SETUP_AND_TEST.md`
- Completion: `COMPLETION_SUMMARY.md`

---

## Troubleshooting

### "Table doesn't exist"
→ Run Step 1 (Create Tables)

### "No recipes found"
→ Run Step 2 (Load Data)

### Server won't start
→ Check: `pkill -f uvicorn` then start again

### Import errors
→ Activate venv: `source venv/bin/activate`

---

## What's Included

- **15 Recipes**: Bangladeshi dishes
- **36+ Products**: Meat, fish, vegetables, rice, spices
- **4 AI Agents**: Orchestrator, Chef, Product, Support
- **Beautiful Responses**: Emojis, formatting, structure
- **Smart Understanding**: Natural language queries

---

## Status Check

```bash
# Check if tables exist
python -c "
from backend.database.connection import get_supabase_client
c = get_supabase_client()
print('Products:', len(c.table('products').select('*').execute().data))
print('Recipes:', len(c.table('documents').select('*').execute().data))
"
```

---

**Need Help?** Check `FINAL_SETUP_AND_TEST.md` for detailed guide!
