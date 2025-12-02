import { ShoppingCart, MapPin } from 'lucide-react';

export function Header() {
    return (
        <header className="bg-gradient-to-r from-orange-400 to-orange-500 shadow-md sticky top-0 z-40">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center space-x-8">
                        <div className="flex items-center">
                            <ShoppingCart className="h-8 w-8 text-white" />
                            <span className="ml-2 text-2xl font-bold text-white">recipe</span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        <button className="flex items-center space-x-2 px-4 py-2 text-white hover:bg-orange-600 rounded-lg transition-colors">
                            <MapPin className="h-5 w-5" />
                            <span className="hidden sm:inline">Dhaka</span>
                        </button>
                        <select className="px-3 py-2 rounded-lg bg-white text-gray-700 font-medium border-2 border-orange-200 focus:outline-none focus:border-orange-400">
                            <option>EN</option>
                            <option>বাংলা</option>
                        </select>
                        <button className="px-6 py-2 bg-white text-orange-500 font-semibold rounded-lg hover:bg-orange-50 transition-colors">
                            Login
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
}
