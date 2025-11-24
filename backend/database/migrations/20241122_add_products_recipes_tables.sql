-- Migration: Add products, recipes, and policies tables with vector support

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    category TEXT,
    image_url TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    ingredients JSONB NOT NULL, -- Array of {product_id, quantity, unit}
    instructions TEXT[] NOT NULL,
    prep_time INTEGER, -- in minutes
    cooking_time INTEGER, -- in minutes
    serving_size INTEGER,
    image_url TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Policies table
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_embedding ON products USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

CREATE INDEX IF NOT EXISTS idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_recipes_ingredients ON recipes USING GIN (ingredients);

CREATE INDEX IF NOT EXISTS idx_policies_embedding ON policies USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_policies_category ON policies(category);

-- Search functions for each table
CREATE OR REPLACE FUNCTION match_products(
    query_embedding VECTOR(384),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    price NUMERIC(10,2),
    category TEXT,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        p.id,
        p.name,
        p.description,
        p.price,
        p.category,
        1 - (p.embedding <=> query_embedding) AS similarity
    FROM products p
    WHERE 1 - (p.embedding <=> query_embedding) > match_threshold
    ORDER BY p.embedding <=> query_embedding
    LIMIT match_count;
$$;

CREATE OR REPLACE FUNCTION match_recipes(
    query_embedding VECTOR(384),
    match_threshold FLOAT,
    match_count INT,
    available_products UUID[] DEFAULT '{}'
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    ingredients JSONB,
    instructions TEXT[],
    prep_time INTEGER,
    cooking_time INTEGER,
    serving_size INTEGER,
    image_url TEXT,
    similarity FLOAT,
    matching_ingredients INTEGER,
    missing_ingredients JSONB
)
LANGUAGE SQL STABLE
AS $$
    WITH recipe_matches AS (
        SELECT
            r.*,
            1 - (r.embedding <=> query_embedding) AS similarity,
            (
                SELECT COUNT(*)::INTEGER
                FROM jsonb_array_elements(r.ingredients) AS i
                WHERE (i->>'product_id')::UUID = ANY(available_products)
            ) AS matching_ingredients,
            (
                SELECT jsonb_agg(i)
                FROM jsonb_array_elements(r.ingredients) AS i
                WHERE NOT ((i->>'product_id')::UUID = ANY(available_products))
            ) AS missing_ingredients
        FROM recipes r
        WHERE 1 - (r.embedding <=> query_embedding) > match_threshold
        ORDER BY r.embedding <=> query_embedding
        LIMIT match_count
    )
    SELECT * FROM recipe_matches
    ORDER BY matching_ingredients DESC, similarity DESC;
$$;

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
