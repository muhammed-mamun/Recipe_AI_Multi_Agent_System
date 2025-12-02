# 🚀 Quick Setup Guide - Get Recipes Working in 5 Minutes!

## Step 1: Create Database Tables (2 minutes)

### Option A: Via Supabase Dashboard (Recommended)

1. **Open Supabase SQL Editor**
   - Go to: https://supabase.com/dashboard/project/pozqlghiwukecwtuhbjh
   - Click **"SQL Editor"** in the left sidebar
   - Click **"New Query"**

2. **Copy and Paste this SQL:**

```sql
-- Enable the pgvector extension to work with embedding vectors
CREATE EXTENSION IF NOT EXISTS vector;

-- Table to store products (inventory)
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  price NUMERIC NOT NULL,
  stock_quantity INT NOT NULL DEFAULT 0,
  category TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for LangChain Vector Store (standard schema)
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT,
  metadata JSONB,
  embedding VECTOR(384)
);

-- Function to search for documents
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

3. **Click "RUN"** button (bottom right)

4. **Verify Success**
   - You should see "Success. No rows returned"
   - Check **"Table Editor"** - you should see `products` and `documents` tables

---

## Step 2: Load Data (3 minutes)

Run this command in your terminal:

```bash
cd /home/mamunhossain/Projects/recipe/recipe_AI_Multi_Agent_System
source venv/bin/activate
python backend/scripts/setup_complete_system.py
```

You should see:
```
✅ Products in database: 36
✅ Recipes in database: 15
🎉 SETUP COMPLETE!
```

---

## Step 3: Test the System!

Restart the backend server:

```bash
# Stop existing server
pkill -f uvicorn

# Start fresh
cd /home/mamunhossain/Projects/recipe/recipe_AI_Multi_Agent_System
source venv/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Recipe Queries:

```bash
# Test 1: Recipe with ingredients
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have chicken and rice. What can I cook?"}'

# Test 2: General recipe request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me fish recipes"}'

# Test 3: Product search
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me available meat options"}'
```

---

## What Customers Can Now Ask:

### 🍳 Recipe Queries:
- "I have chicken, rice and onions. What can I cook?"
- "Show me fish recipes"
- "What can I make for dinner?"
- "I want to cook something with potato"
- "Suggest me a dessert recipe"
- "How to make tehari?"
- "Give me a recipe for breakfast"

### 🛒 Product Queries:
- "Show me available meat options"
- "What vegetables do you have?"
- "How much does tomato cost?"
- "Is chicken available?"

### 📞 Support Queries:
- "What is your return policy?"
- "How do I get a refund?"
- "What are your delivery charges?"

---

## Troubleshooting

### Issue: "Table doesn't exist"
**Solution**: Make sure you ran the SQL in Step 1

### Issue: "No recipes found"
**Solution**: Run `python backend/scripts/setup_complete_system.py` again

### Issue: "Connection error"
**Solution**: Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`

---

## What's Included:

### 15 Authentic Bangladeshi Recipes:
1. 🍛 Old Dhaka Beef Tehari
2. 🐟 Rui Macher Dopeyaja (Fish Curry)
3. 🍗 Biye Barir Chicken Roast
4. 🍚 Patla Khichuri
5. 🥔 Aloo Bhorta
6. 🍆 Begun Bhaji
7. 🥘 Panch Mishali Sabji
8. 🍳 Dimer Omelette Curry
9. 🍰 Sujir Halwa
10. And 6 more!

### 36+ Products:
- Chicken (Sonali, Broiler)
- Fish (Rui, Ilish, Pabda)
- Vegetables (Potato, Tomato, Onion, etc.)
- Rice varieties
- Spices and more!

---

**That's it! Your AI system is ready to suggest recipes and help customers! 🎉**
