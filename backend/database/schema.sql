-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    category TEXT,
    image_url TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    ingredients JSONB NOT NULL,
    instructions TEXT[] NOT NULL,
    prep_time INTEGER,
    cooking_time INTEGER,
    serving_size INTEGER,
    image_url TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create policies table
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_embedding 
ON products USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_recipes_embedding 
ON recipes USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_policies_embedding 
ON policies USING ivfflat (embedding vector_cosine_ops);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_products_modtime
BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_recipes_modtime
BEFORE UPDATE ON recipes
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_policies_modtime
BEFORE UPDATE ON policies
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- ============================================
-- RPC FUNCTIONS FOR SEMANTIC SEARCH
-- ============================================

-- Match Products
create or replace function match_products (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  name text,
  description text,
  price numeric,
  stock_quantity int,
  category text,
  image_url text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    products.id,
    products.name,
    products.description,
    products.price,
    products.stock_quantity,
    products.category,
    products.image_url,
    1 - (products.embedding <=> query_embedding) as similarity
  from products
  where 1 - (products.embedding <=> query_embedding) > match_threshold
  order by products.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Match Recipes (Simplified)
create or replace function match_recipes (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  available_products text[]
)
returns table (
  id uuid,
  name text,
  description text,
  ingredients jsonb,
  instructions text[],
  prep_time int,
  cooking_time int,
  serving_size int,
  image_url text,
  similarity float,
  matching_ingredients jsonb,
  missing_ingredients jsonb
)
language plpgsql
as $$
begin
  return query
  select
    recipes.id,
    recipes.name,
    recipes.description,
    recipes.ingredients,
    recipes.instructions,
    recipes.prep_time,
    recipes.cooking_time,
    recipes.serving_size,
    recipes.image_url,
    1 - (recipes.embedding <=> query_embedding) as similarity,
    '[]'::jsonb as matching_ingredients, -- Placeholder for complex logic
    recipes.ingredients as missing_ingredients -- Placeholder
  from recipes
  where 1 - (recipes.embedding <=> query_embedding) > match_threshold
  order by recipes.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Match Policies (using match_documents signature if needed, or specific one)
-- operations.py calls match_documents for policies.
-- We need to ensure match_documents exists or update operations.py to use match_policies.
-- Since operations.py uses match_documents, let's define match_documents to search policies?
-- Or better, define match_documents to search a 'documents' table if it exists, OR define match_policies and update operations.py.
-- The user's SQL created 'policies', not 'documents'.
-- operations.py line 182 calls 'match_documents'.
-- We should probably define match_documents to search 'policies' for now, or create a 'documents' table.
-- But the user wants 'policies'.
-- I will define match_documents to search 'policies' table columns, mapping them to document fields.

create or replace function match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    policies.id,
    policies.content,
    jsonb_build_object('title', policies.title, 'category', policies.category) as metadata,
    1 - (policies.embedding <=> query_embedding) as similarity
  from policies
  where 1 - (policies.embedding <=> query_embedding) > match_threshold
  order by policies.embedding <=> query_embedding
  limit match_count;
end;
$$;
