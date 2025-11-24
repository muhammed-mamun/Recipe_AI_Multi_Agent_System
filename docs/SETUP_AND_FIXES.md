# Chaldal AI Multi-Agent System - Setup and Fixes

## Issues Found and Fixed

### 1. Environment Variables Not Loading
**Problem**: The `.env` file in the `backend/` directory was not being loaded when running the server from the project root.

**Fix**: Updated `backend/database/connection.py` and `backend/model.py` to explicitly load the `.env` file from the backend directory:
```python
backend_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(backend_dir, '.env'))
```

### 2. Database Tables Not Created
**Problem**: The Supabase database tables (`products` and `documents`) haven't been created yet, causing errors when trying to search for recipes or products.

**Solution**: Created a new script `backend/scripts/setup_database.py` to help with database setup.

### 3. Supabase Query API Compatibility
**Problem**: The seed data script used deprecated Supabase query methods (`.neq()` with impossible UUID).

**Fix**: Updated `backend/scripts/seed_data.py` to use `.gte()` with proper error handling.

### 4. Missing Error Handling
**Problem**: No graceful error handling when database tables don't exist.

**Fix**: Added try-catch blocks in `backend/agents/chef.py` to return helpful error messages.

## Current System Status

### ✅ Working Features:
1. **Backend API Server**: Running on http://localhost:8000
2. **Health Check**: Endpoint working correctly
3. **Support Agent**: Handles customer support queries (return policy, refund, delivery, contact info)
4. **General Chat**: Can answer general questions
5. **Intent Classification**: Correctly routes queries to appropriate agents

### ⚠️ Pending Setup:
1. **Database Tables**: Need to be created in Supabase (see instructions below)
2. **Recipe Search**: Will work once database is set up
3. **Product Search**: Placeholder - needs implementation
4. **Inventory Check**: Will work once database is set up

## Database Setup Instructions

### Step 1: Create Tables in Supabase
1. Go to your Supabase project: https://pozqlghiwukecwtuhbjh.supabase.co
2. Navigate to **SQL Editor**
3. Copy and paste the SQL from `backend/database/schema.sql`
4. Click **Run** to execute

### Step 2: Seed Data
After creating the tables, run:
```bash
cd /home/mamunhossain/Projects/chaldal/Chaldal_AI_Multi_Agent_System
source venv/bin/activate
python backend/scripts/seed_data.py
```

This will populate:
- Products table with sample grocery items from `backend/data/products.json`
- Documents table with recipe embeddings from `backend/data/recipes.json`

## Testing the AI Agent

### Test Commands:

1. **General Chat**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! Can you help me?"}'
```

2. **Support Query - Return Policy**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your return policy?"}'
```

3. **Support Query - Refund**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your refund policy?"}'
```

4. **Support Query - Contact**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I contact customer support?"}'
```

5. **Support Query - Delivery**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you offer express delivery? What are the charges?"}'
```

6. **Cooking Query** (after database setup):
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have chicken, rice and onions. What can I cook?"}'
```

7. **Product Query** (placeholder response):
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does tomato cost?"}'
```

## Conversation Examples

### Example 1: Support Query
**Customer**: "What is your return policy?"

**AI Response**:
```
### Chaldal Return Policy

- **No Questions Asked**: Return any item to the delivery person at the door for a full refund if dissatisfied.
- **Perishables** (Fish, Meat, Veg): Report issues within 24 hours of delivery.
- **Non-Perishables** (Packaged Goods): Return unopened items within 7 days.
- **How to Return**: Call **16716** or use the "Issue Report" button in Order History.

For returns leading to refunds, check our [Return Policy](instructions#return-policy). Need help? Call **16716** or use the app's "Issue Report".
```

### Example 2: Delivery Query
**Customer**: "Do you offer express delivery? What are the charges?"

**AI Response**:
```
### Express Delivery
- **Availability**: Yes, in select areas (1-hour delivery).
- **Charges**: Free for orders over ৳400 (standard offer, may vary). Regular charge: ৳29-49.

For availability in your area, check the app or call 16716.
```

### Example 3: Contact Query
**Customer**: "How do I contact customer support?"

**AI Response**:
```
Hi! You can contact Chaldal Customer Support via:

- **Hotline**: 16716 (Available 8 AM - 11 PM)
- **Email**: support@chaldal.com
- **Live Chat**: Available in the app menu
```

## Architecture Overview

### Multi-Agent System
1. **Orchestrator Agent**: Routes queries to appropriate specialized agents
2. **Chef Agent**: Handles cooking queries, recipe suggestions, ingredient checks
3. **Support Agent**: Handles customer service queries (policies, delivery, contact)

### Intent Classification
The system automatically classifies queries into:
- **COOKING_QUERY**: Recipe requests, ingredient-based questions
- **SUPPORT_QUERY**: Policy, delivery, refund, contact questions
- **PRODUCT_QUERY**: Product availability and pricing questions
- **OTHER**: General chat

## Running the System

### Start Backend:
```bash
cd /home/mamunhossain/Projects/chaldal/Chaldal_AI_Multi_Agent_System
source venv/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (in another terminal):
```bash
cd /home/mamunhossain/Projects/chaldal/Chaldal_AI_Multi_Agent_System/frontend
npm run dev
```

Then open http://localhost:3000 in your browser.

## Next Steps

1. **Set up database**: Follow the database setup instructions above
2. **Test recipe search**: After database setup, test cooking queries
3. **Implement product search**: Add actual product search functionality
4. **Frontend integration**: Connect the frontend to the working backend
5. **Add more recipes**: Expand the recipe database
6. **Enhance inventory**: Add more products to the inventory

## Notes

- The AI uses Grok-4.1-fast model via OpenRouter
- Environment variables are in `backend/.env`
- All dependencies are already installed in the virtual environment
- The system gracefully handles missing database tables with informative error messages
