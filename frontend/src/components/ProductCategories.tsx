import { ChevronRight } from 'lucide-react';

const categories = [
    {
        name: 'Fruits & Vegetables',
        image: 'https://images.pexels.com/photos/1300972/pexels-photo-1300972.jpeg',
    },
    {
        name: 'Meat & Fish',
        image: 'https://images.pexels.com/photos/3296434/pexels-photo-3296434.jpeg',
    },
    {
        name: 'Cooking',
        image: 'https://images.pexels.com/photos/4252140/pexels-photo-4252140.jpeg',
    },
    {
        name: 'Beverages',
        image: 'https://images.pexels.com/photos/5946072/pexels-photo-5946072.jpeg',
    },
    {
        name: 'Home & Cleaning',
        image: 'https://images.pexels.com/photos/4239091/pexels-photo-4239091.jpeg',
    },
    {
        name: 'Pest Control',
        image: 'https://images.pexels.com/photos/4099467/pexels-photo-4099467.jpeg',
    },
    {
        name: 'Snacks',
        image: 'https://images.pexels.com/photos/1583884/pexels-photo-1583884.jpeg',
    },
    {
        name: 'Dairy & Eggs',
        image: 'https://images.pexels.com/photos/4109998/pexels-photo-4109998.jpeg',
    },
];

export function ProductCategories() {
    return (
        <section className="py-16 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-bold text-gray-900">Popular Categories</h2>
                    <button className="flex items-center space-x-2 text-orange-500 hover:text-orange-600 font-semibold transition-colors">
                        <span>View All</span>
                        <ChevronRight className="h-5 w-5" />
                    </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8 gap-4">
                    {categories.map((category, index) => (
                        <button
                            key={index}
                            className="group relative overflow-hidden rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                        >
                            <div className="aspect-square">
                                <img
                                    src={category.image}
                                    alt={category.name}
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
                                <div className="absolute bottom-0 left-0 right-0 p-3">
                                    <p className="text-white font-semibold text-sm text-center leading-tight">
                                        {category.name}
                                    </p>
                                </div>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </section>
    );
}
