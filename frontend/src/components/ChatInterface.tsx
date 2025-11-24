"use client";

import { useState, useRef, useEffect } from 'react';
import { ChefHat, Send, Loader2, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { sendChatMessage } from '../services/aiService';
import type { Message } from '../types';
import { RecipeCard } from './RecipeCard';

export function ChatInterface() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const [cartModal, setCartModal] = useState<{ items: any[], total: number } | null>(null);
    const [selectedCartItems, setSelectedCartItems] = useState<any[]>([]);
    const [dietaryPreferences, setDietaryPreferences] = useState<string[]>([]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!inputMessage.trim() || isLoading) return;

        if (messages.length === 0) {
            setIsOpen(true);
        }

        // Append dietary preferences to the message if any are selected
        let messageToSend = inputMessage.trim();
        if (dietaryPreferences.length > 0) {
            messageToSend += ` (Dietary preferences: ${dietaryPreferences.join(', ')})`;
        }

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputMessage.trim(), // Display original message without preferences
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const response = await sendChatMessage(messageToSend); // Send with preferences

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.message,
                timestamp: new Date(),
                recipes: response.recipes,
                missingIngredients: response.missingIngredients,
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again!',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <>
            {isOpen && messages.length > 0 && (
                <div className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm" onClick={() => setIsOpen(false)} />
            )}

            <div className={`fixed left-1/2 transform -translate-x-1/2 z-40 w-full max-w-5xl px-4 transition-all duration-500 ease-out ${isOpen && messages.length > 0
                ? 'bottom-6 top-6'
                : 'bottom-6'
                }`}>
                <div className="relative h-full flex flex-col">
                    <div className="absolute -inset-2 bg-gradient-to-r from-orange-400 via-rose-400 to-orange-500 rounded-[2rem] blur-xl opacity-20 group-hover:opacity-40 transition-all duration-500 animate-pulse"></div>

                    <div className={`relative bg-white/95 backdrop-blur-xl shadow-2xl border border-orange-100/50 transition-all duration-500 flex flex-col ${isOpen && messages.length > 0
                        ? 'rounded-3xl h-full'
                        : 'rounded-[2rem] hover:border-orange-200 hover:shadow-orange-100/50'
                        }`}>

                        {isOpen && messages.length > 0 && (
                            <>
                                <div className="bg-gradient-to-r from-orange-500 via-orange-600 to-orange-500 px-6 py-4 flex items-center justify-between rounded-t-3xl flex-shrink-0">
                                    <div className="flex items-center space-x-3">
                                        <div className="bg-white/20 p-2.5 rounded-full backdrop-blur-sm">
                                            <ChefHat className="h-5 w-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="text-white font-bold text-lg">Chaldal AI Assistant</h3>
                                            <p className="text-orange-50 text-sm">Recipe suggestions & product queries</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setIsOpen(false);
                                        }}
                                        className="text-white hover:bg-white/20 p-2 rounded-full transition-all duration-200 hover:rotate-90"
                                    >
                                        ✕
                                    </button>
                                </div>

                                {/* Dietary Preferences Filter */}
                                <div className="bg-orange-50 px-6 py-3 border-b border-orange-100 flex-shrink-0">
                                    <div className="flex items-center gap-3 flex-wrap">
                                        <span className="text-sm font-semibold text-gray-700">Dietary Preferences:</span>
                                        {['Vegetarian', 'Halal', 'Gluten-Free'].map((pref) => (
                                            <button
                                                key={pref}
                                                onClick={() => {
                                                    setDietaryPreferences(prev =>
                                                        prev.includes(pref)
                                                            ? prev.filter(p => p !== pref)
                                                            : [...prev, pref]
                                                    );
                                                }}
                                                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${dietaryPreferences.includes(pref)
                                                    ? 'bg-orange-500 text-white shadow-md scale-105'
                                                    : 'bg-white text-gray-600 hover:bg-orange-100 border border-orange-200'
                                                    }`}
                                            >
                                                {dietaryPreferences.includes(pref) && '✓ '}
                                                {pref}
                                            </button>
                                        ))}
                                        {dietaryPreferences.length > 0 && (
                                            <button
                                                onClick={() => setDietaryPreferences([])}
                                                className="text-xs text-orange-600 hover:text-orange-700 font-medium underline"
                                            >
                                                Clear all
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </>
                        )}

                        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-orange-50/30 to-white">
                            {messages.map(message => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] ${message.role === 'user'
                                            ? 'bg-orange-500 text-white'
                                            : 'bg-white text-gray-800 shadow-md'
                                            } rounded-2xl px-5 py-3`}
                                    >
                                        {message.role === 'user' ? (
                                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                        ) : (
                                            <>
                                                {/* Split content by BUY_INGREDIENTS tags and render inline */}
                                                {(() => {
                                                    const content = message.content;
                                                    const parts: JSX.Element[] = [];
                                                    let lastIndex = 0;
                                                    let partKey = 0;

                                                    // Find all BUY_INGREDIENTS tags
                                                    let searchIndex = 0;
                                                    while (true) {
                                                        const tagStart = content.indexOf('[BUY_INGREDIENTS:', searchIndex);
                                                        if (tagStart === -1) {
                                                            // No more tags, add remaining content
                                                            const remainingContent = content.substring(lastIndex);
                                                            if (remainingContent.trim()) {
                                                                parts.push(
                                                                    <div key={`text-${partKey++}`} className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-h3:text-lg prose-h3:font-bold prose-h3:mb-2 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:my-2 prose-li:text-gray-700">
                                                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                                            {remainingContent}
                                                                        </ReactMarkdown>
                                                                    </div>
                                                                );
                                                            }
                                                            break;
                                                        }

                                                        // Add content before this tag
                                                        const beforeTag = content.substring(lastIndex, tagStart);
                                                        if (beforeTag.trim()) {
                                                            parts.push(
                                                                <div key={`text-${partKey++}`} className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-h3:text-lg prose-h3:font-bold prose-h3:mb-2 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:my-2 prose-li:text-gray-700">
                                                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                                        {beforeTag}
                                                                    </ReactMarkdown>
                                                                </div>
                                                            );
                                                        }

                                                        // Extract JSON from tag
                                                        const jsonStart = content.indexOf('{', tagStart);
                                                        if (jsonStart === -1) {
                                                            searchIndex = tagStart + 1;
                                                            continue;
                                                        }

                                                        // Count braces to find matching closing brace
                                                        let braceCount = 0;
                                                        let jsonEnd = jsonStart;
                                                        for (let i = jsonStart; i < content.length; i++) {
                                                            if (content[i] === '{') braceCount++;
                                                            if (content[i] === '}') braceCount--;
                                                            if (braceCount === 0) {
                                                                jsonEnd = i + 1;
                                                                break;
                                                            }
                                                        }

                                                        const jsonStr = content.substring(jsonStart, jsonEnd);

                                                        try {
                                                            const data = JSON.parse(jsonStr);

                                                            if (data.items && data.items.length > 0) {
                                                                parts.push(
                                                                    <div key={`button-${partKey++}`} className="mt-4 p-4 bg-gradient-to-r from-orange-50 to-orange-100 border-2 border-orange-300 rounded-xl">
                                                                        <div className="flex items-center justify-between">
                                                                            <div className="flex-1">
                                                                                <p className="font-bold text-orange-900 text-sm mb-1">🛒 Missing Ingredients</p>
                                                                                <p className="text-xs text-orange-700">
                                                                                    {data.items.map((item: any) => item.name).join(', ')}
                                                                                </p>
                                                                            </div>
                                                                            <button
                                                                                onClick={() => {
                                                                                    setSelectedCartItems(data.items);
                                                                                    setCartModal({ items: data.items, total: data.total });
                                                                                }}
                                                                                className="ml-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-6 py-2.5 rounded-full text-sm font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2 whitespace-nowrap"
                                                                            >
                                                                                <span>Buy All</span>
                                                                                <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">৳{data.total}</span>
                                                                            </button>
                                                                        </div>
                                                                    </div>
                                                                );
                                                            }
                                                        } catch (e) {
                                                            console.error('Failed to parse buy ingredients:', e);
                                                        }

                                                        // Find the end of the tag (closing ])
                                                        const tagEnd = content.indexOf(']', jsonEnd);
                                                        lastIndex = tagEnd + 1;
                                                        searchIndex = lastIndex;
                                                    }

                                                    return parts;
                                                })()}
                                            </>
                                        )}

                                        {message.recipes && message.recipes.length > 0 && (
                                            <div className="mt-4 space-y-3">
                                                {message.recipes.map(recipe => (
                                                    <RecipeCard
                                                        key={recipe.id}
                                                        recipe={recipe}
                                                        missingIngredients={message.missingIngredients}
                                                    />
                                                ))}
                                            </div>
                                        )}

                                        <p className="text-xs mt-2 opacity-70">
                                            {message.timestamp.toLocaleTimeString([], {
                                                hour: '2-digit',
                                                minute: '2-digit',
                                            })}
                                        </p>
                                    </div>
                                </div>
                            ))}

                            {isLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-white rounded-2xl px-5 py-3 shadow-md">
                                        <Loader2 className="h-5 w-5 text-orange-500 animate-spin" />
                                    </div>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>

                        <div className={`flex items-center gap-3 px-6 py-4 flex-shrink-0 ${isOpen && messages.length > 0 ? 'border-t border-orange-100' : ''
                            }`}>
                            <div className="flex items-center gap-2.5 text-orange-500 flex-shrink-0">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-orange-400 rounded-full blur-md opacity-40"></div>
                                    <div className="relative p-2 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full">
                                        <ChefHat className="h-5 w-5 text-white" />
                                    </div>
                                </div>
                                <Sparkles className="h-4 w-4 animate-pulse text-orange-400" />
                            </div>
                            <input
                                ref={inputRef}
                                type="text"
                                value={inputMessage}
                                onChange={e => setInputMessage(e.target.value)}
                                onKeyPress={handleKeyPress}
                                onClick={() => messages.length > 0 && setIsOpen(true)}
                                placeholder={dietaryPreferences.length > 0
                                    ? `Ask for ${dietaryPreferences.join(', ')} recipes...`
                                    : "Ask Chaldal AI anything - recipes, products, cooking tips..."}
                                className="flex-1 py-2.5 px-4 bg-transparent text-gray-800 placeholder-gray-400 focus:outline-none text-sm font-medium"
                                disabled={isLoading}
                            />
                            {dietaryPreferences.length > 0 && (
                                <div className="flex items-center gap-1 px-2 py-1 bg-orange-100 rounded-full">
                                    <span className="text-xs font-semibold text-orange-700">
                                        {dietaryPreferences.length} filter{dietaryPreferences.length > 1 ? 's' : ''}
                                    </span>
                                </div>
                            )}
                            <button
                                onClick={handleSend}
                                disabled={!inputMessage.trim() || isLoading}
                                className="relative group/btn bg-gradient-to-r from-orange-500 via-orange-600 to-orange-500 bg-size-200 hover:bg-pos-100 text-white px-7 py-3 rounded-full transition-all duration-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2.5 shadow-lg hover:shadow-2xl hover:shadow-orange-300/50 hover:scale-105 transform overflow-hidden"
                                style={{ backgroundSize: '200% 100%' }}
                            >
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-700"></div>
                                {isLoading ? (
                                    <Loader2 className="h-4 w-4 animate-spin relative z-10" />
                                ) : (
                                    <>
                                        <span className="font-bold text-sm hidden sm:inline relative z-10">Ask AI</span>
                                        <Send className="h-4 w-4 relative z-10" />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div >

            {/* Beautiful Cart Modal */}
            {
                cartModal && (
                    <div
                        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn"
                        onClick={() => setCartModal(null)}
                    >
                        <div
                            className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 animate-slideUp"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Header */}
                            <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-t-2xl">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="bg-white/20 p-2 rounded-full">
                                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                            </svg>
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-bold">Add to Cart</h3>
                                            <p className="text-sm text-orange-100">{cartModal.items.length} items</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setCartModal(null)}
                                        className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
                                    >
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            </div>

                            {/* Items List */}
                            <div className="p-6 max-h-96 overflow-y-auto">
                                {selectedCartItems.length > 0 ? (
                                    <>
                                        <div className="space-y-3">
                                            {selectedCartItems.map((item: any, index: number) => (
                                                <div
                                                    key={index}
                                                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
                                                >
                                                    <div className="flex items-center gap-3 flex-1">
                                                        <div className="bg-orange-100 text-orange-600 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">
                                                            {index + 1}
                                                        </div>
                                                        <span className="font-medium text-gray-800">{item.name}</span>
                                                    </div>
                                                    <div className="flex items-center gap-3">
                                                        <span className="font-bold text-orange-600">৳{item.price}</span>
                                                        <button
                                                            onClick={() => {
                                                                setSelectedCartItems(prev => prev.filter((_, i) => i !== index));
                                                            }}
                                                            className="opacity-0 group-hover:opacity-100 transition-opacity bg-red-100 hover:bg-red-200 text-red-600 rounded-full p-1.5 hover:scale-110 transform duration-200"
                                                            title="Remove item"
                                                        >
                                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                            </svg>
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>

                                        {/* Total */}
                                        <div className="mt-6 pt-4 border-t-2 border-gray-200">
                                            <div className="flex items-center justify-between">
                                                <span className="text-lg font-bold text-gray-800">Total Amount</span>
                                                <span className="text-2xl font-bold text-orange-600">
                                                    ৳{selectedCartItems.reduce((sum, item) => sum + item.price, 0)}
                                                </span>
                                            </div>
                                        </div>
                                    </>
                                ) : (
                                    <div className="text-center py-8">
                                        <div className="text-gray-400 mb-2">
                                            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                                            </svg>
                                        </div>
                                        <p className="text-gray-500 font-medium">No items selected</p>
                                        <p className="text-gray-400 text-sm mt-1">Add items to continue</p>
                                    </div>
                                )}
                            </div>

                            {/* Action Buttons */}
                            <div className="p-6 bg-gray-50 rounded-b-2xl flex gap-3">
                                <button
                                    onClick={() => {
                                        setCartModal(null);
                                        setSelectedCartItems([]);
                                    }}
                                    className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-bold rounded-xl hover:bg-gray-100 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={() => {
                                        if (selectedCartItems.length === 0) return;
                                        const total = selectedCartItems.reduce((sum, item) => sum + item.price, 0);
                                        alert(`Items added to cart! 🎉\n\n${selectedCartItems.map(item => `• ${item.name} - ৳${item.price}`).join('\n')}\n\nTotal: ৳${total}\n\nThis would integrate with your cart system.`);
                                        setCartModal(null);
                                        setSelectedCartItems([]);
                                    }}
                                    disabled={selectedCartItems.length === 0}
                                    className={`flex-1 px-6 py-3 font-bold rounded-xl shadow-lg transition-all duration-200 ${selectedCartItems.length === 0
                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 hover:shadow-xl transform hover:scale-105'
                                        }`}
                                >
                                    Add to Cart {selectedCartItems.length > 0 && `(${selectedCartItems.length})`}
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            <style jsx>{`
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { 
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to { 
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                .animate-fadeIn {
                    animation: fadeIn 0.2s ease-out;
                }
                .animate-slideUp {
                    animation: slideUp 0.3s ease-out;
                }
            `}</style>
        </>
    );
}
