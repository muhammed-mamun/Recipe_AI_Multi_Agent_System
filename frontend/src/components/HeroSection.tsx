import { Search } from 'lucide-react';

export function HeroSection() {
    return (
        <section className="bg-gradient-to-br from-yellow-100 via-orange-50 to-yellow-100 py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    <div>
                        <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6">
                            Grocery Delivered at your Doorstep
                        </h1>

                        <div className="relative mb-8">
                            <input
                                type="text"
                                placeholder="Search for products (e.g. eggs, milk, potato)"
                                className="w-full px-6 py-4 rounded-full border-2 border-gray-200 focus:border-orange-400 focus:outline-none text-lg shadow-lg"
                            />
                            <button className="absolute right-2 top-1/2 transform -translate-y-1/2 p-3 bg-orange-500 hover:bg-orange-600 text-white rounded-full transition-colors">
                                <Search className="h-6 w-6" />
                            </button>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-center">
                            <div className="bg-white p-4 rounded-xl shadow-md">
                                <span className="text-3xl font-bold text-orange-500">+15000</span>
                                <p className="text-gray-600 font-medium">products to shop from</p>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-md">
                                <span className="text-3xl font-bold text-orange-500">1 hour</span>
                                <p className="text-gray-600 font-medium">delivery time</p>
                            </div>
                        </div>
                    </div>

                    <div className="hidden lg:block">
                        <div className="grid grid-cols-2 gap-4">
                            <img
                                src="https://images.pexels.com/photos/4348401/pexels-photo-4348401.jpeg"
                                alt="Delivery person"
                                className="rounded-2xl shadow-xl h-64 w-full object-cover"
                            />
                            <img
                                src="https://images.pexels.com/photos/3962285/pexels-photo-3962285.jpeg"
                                alt="Fresh vegetables"
                                className="rounded-2xl shadow-xl h-64 w-full object-cover mt-8"
                            />
                            <img
                                src="https://images.pexels.com/photos/264636/pexels-photo-264636.jpeg"
                                alt="Grocery aisle"
                                className="rounded-2xl shadow-xl h-64 w-full object-cover -mt-8"
                            />
                            <img
                                src="https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"
                                alt="Fresh produce"
                                className="rounded-2xl shadow-xl h-64 w-full object-cover"
                            />
                        </div>
                    </div>
                </div>

                <div className="mt-12 grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white p-6 rounded-xl shadow-md text-center">
                        <p className="text-sm text-gray-600">Pay</p>
                        <p className="text-lg font-bold text-orange-500">after</p>
                        <p className="text-sm text-gray-600">receiving products</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-md text-center">
                        <p className="text-lg font-bold text-orange-500">Get offers that</p>
                        <p className="text-lg font-bold text-orange-500">Save Money</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-md text-center">
                        <p className="text-sm text-gray-600">Get your delivery within</p>
                        <p className="text-lg font-bold text-orange-500">1 hour</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-md text-center">
                        <p className="text-lg font-bold text-orange-500">Save Money</p>
                        <p className="text-sm text-gray-600">with our offers</p>
                    </div>
                </div>
            </div>
        </section>
    );
}
