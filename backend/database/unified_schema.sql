-- ============================================
-- CHALDAL AI MULTI-AGENT SYSTEM DATABASE
-- Complete Schema with Vector Embeddings
-- ============================================

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- TABLE 1: PRODUCTS (Inventory Management)
-- ============================================
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  price NUMERIC NOT NULL,
  stock_quantity INT NOT NULL DEFAULT 0,
  category TEXT,
  description TEXT,
  unit TEXT DEFAULT 'unit',
  image_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

-- ============================================
-- TABLE 2: KNOWLEDGE BASE (Vector Store)
-- Universal table for ALL AI-searchable content
-- Includes: Recipes, Policies, FAQs, Product Descriptions
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_base (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_type TEXT NOT NULL, -- 'recipe', 'policy', 'faq', 'product_info'
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_base(content_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- ============================================
-- VECTOR SEARCH FUNCTION
-- Universal semantic search across all content
-- ============================================
CREATE OR REPLACE FUNCTION search_knowledge (
  query_embedding VECTOR(384),
  content_type_filter TEXT DEFAULT NULL,
  match_threshold FLOAT DEFAULT 0.0,
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id UUID,
  content_type TEXT,
  title TEXT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    knowledge_base.id,
    knowledge_base.content_type,
    knowledge_base.title,
    knowledge_base.content,
    knowledge_base.metadata,
    1 - (knowledge_base.embedding <=> query_embedding) AS similarity
  FROM knowledge_base
  WHERE 
    (content_type_filter IS NULL OR knowledge_base.content_type = content_type_filter)
    AND (1 - (knowledge_base.embedding <=> query_embedding)) > match_threshold
  ORDER BY knowledge_base.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================
-- LEGACY COMPATIBILITY
-- Keep documents table for backward compatibility
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT,
  metadata JSONB,
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

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

-- ============================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER update_products_updated_at 
  BEFORE UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at 
  BEFORE UPDATE ON knowledge_base
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- HELPER VIEWS
-- ============================================

-- View for recipes only
CREATE OR REPLACE VIEW recipes_view AS
SELECT 
  id,
  title,
  content,
  metadata,
  created_at
FROM knowledge_base
WHERE content_type = 'recipe';

-- View for policies only
CREATE OR REPLACE VIEW policies_view AS
SELECT 
  id,
  title,
  content,
  metadata,
  created_at
FROM knowledge_base
WHERE content_type = 'policy';

-- View for FAQs only
CREATE OR REPLACE VIEW faqs_view AS
SELECT 
  id,
  title,
  content,
  metadata,
  created_at
FROM knowledge_base
WHERE content_type = 'faq';

-- ============================================
-- SUCCESS MESSAGE
-- ============================================
DO $$ 
BEGIN 
  RAISE NOTICE '✅ Chaldal AI Database Schema Created Successfully!';
  RAISE NOTICE '✅ Tables: products, knowledge_base, documents';
  RAISE NOTICE '✅ Vector Search: search_knowledge() function ready';
  RAISE NOTICE '✅ Ready for AI-powered semantic search!';
END $$;
