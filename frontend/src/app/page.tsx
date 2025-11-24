"use client";

import { HeroSection } from "@/components/HeroSection";
import { ProductCategories } from "@/components/ProductCategories";
import { ChatInterface } from "@/components/ChatInterface";

export default function Home() {
    return (
        <main className="min-h-screen bg-gray-50">
            <HeroSection />
            <ProductCategories />
            <ChatInterface />
        </main>
    );
}
