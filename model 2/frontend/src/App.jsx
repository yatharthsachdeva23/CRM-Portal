import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CitizenPortal from './pages/CitizenPortal';
import CommandCenter from './pages/CommandCenter';

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-gray-100 flex flex-col">
                {/* Navigation Bar */}
                <nav className="bg-indigo-600 text-white p-4 shadow-lg">
                    <div className="container mx-auto flex justify-between items-center">
                        <h1 className="text-2xl font-bold tracking-wider">PS-CRM</h1>
                        <div className="space-x-4">
                            <Link to="/" className="hover:text-indigo-200 transition">Citizen Portal</Link>
                            <Link to="/command-center" className="hover:text-indigo-200 transition">Command Center</Link>
                        </div>
                    </div>
                </nav>

                {/* Main Content Area */}
                <main className="flex-1 container mx-auto p-4 overflow-y-auto">
                    <Routes>
                        <Route path="/" element={<CitizenPortal />} />
                        <Route path="/command-center" element={<CommandCenter />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
