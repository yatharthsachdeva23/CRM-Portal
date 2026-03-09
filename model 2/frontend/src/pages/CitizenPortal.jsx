import React, { useState, useEffect } from 'react';
import { Mic, Send, Image as ImageIcon, MapPin, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { submitTicket, fetchAllTickets } from '../services/api';

const CitizenPortal = () => {
    const [description, setDescription] = useState("");
    const [trustScore, setTrustScore] = useState(120);
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [expandedId, setExpandedId] = useState(null);

    const fetchTickets = async () => {
        try {
            // Fetching all tickets since we don't have login, but could filter by citizen
            const { data } = await fetchAllTickets();
            // Assume "Citizen Portal" source tickets belong to us for demo purposes
            setTickets(data.filter(t => t.source === "Citizen Portal"));
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchTickets();
        const interval = setInterval(fetchTickets, 3000); // Live polling
        return () => clearInterval(interval);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!description) return;
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("description", description);
            // Mocking Delhi GPS for demo purposes if browser GPS fails
            formData.append("lat", 28.6139 + (Math.random() - 0.5) * 0.05);
            formData.append("lon", 77.2090 + (Math.random() - 0.5) * 0.05);
            formData.append("source", "Citizen Portal");

            await submitTicket(formData);
            setDescription("");
            setTrustScore(prev => prev + 10); // Gamification
            fetchTickets();
        } catch (error) {
            alert("Error submitting ticket.");
        } finally {
            setLoading(false);
        }
    };

    const getStatusStep = (status) => {
        switch (status) {
            case "Received": return 1;
            case "Assigned": return 2;
            case "On Site": return 3;
            case "Resolved": return 4;
            default: return 1;
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-fade-in-up pb-10">
            <div className="bg-white rounded-xl shadow-md p-6 flex items-center justify-between border-l-4 border-emerald-500">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-800">Welcome, Citizen</h2>
                    <p className="text-gray-500">Your gamified community power</p>
                </div>
                <div className="text-right">
                    <p className="text-sm font-bold text-gray-400 uppercase tracking-wide">Trust Score</p>
                    <p className="text-4xl font-extrabold text-emerald-500 transition-all">{trustScore}</p>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="text-xl font-medium text-gray-800 mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
                    Report an Issue
                </h3>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <textarea
                            className="w-full border border-gray-200 rounded-lg p-3 outline-none focus:ring-2 focus:ring-indigo-400 transition"
                            rows="4"
                            placeholder="Describe the problem... e.g., 'Water pipe burst on Main St.'"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    <div className="flex flex-wrap gap-4">
                        <button type="button" className="flex items-center gap-2 px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50 transition">
                            <MapPin size={18} /> GPS
                        </button>
                        <button type="button" className="flex items-center gap-2 px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50 transition">
                            <ImageIcon size={18} /> Photo
                        </button>
                        <button type="button" className="flex items-center gap-2 px-4 py-2 border rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition border-red-200">
                            <Mic size={18} /> Voice (Bhashini)
                        </button>
                    </div>

                    <button disabled={loading} type="submit" className="w-full flex justify-center items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg shadow-md hover:shadow-lg transition disabled:opacity-50">
                        {loading ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
                        {loading ? 'Submitting...' : 'Submit Ticket'}
                    </button>
                </form>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="text-lg font-medium text-gray-800 mb-4">My Live Tickets</h3>
                {tickets.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No recent tickets.</p>
                ) : (
                    <div className="space-y-4">
                        {tickets.map(ticket => (
                            <div key={ticket.id} className="border rounded-lg p-4  bg-gray-50 transition-all cursor-pointer hover:shadow-sm" onClick={() => setExpandedId(expandedId === ticket.id ? null : ticket.id)}>
                                <div className="flex justify-between items-center">
                                    <div>
                                        <span className="font-bold text-indigo-700">#{ticket.id}</span>
                                        <span className="ml-2 font-semibold text-gray-800">{ticket.category}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-gray-500">
                                        <span className="px-2 py-1 bg-white border rounded text-xs font-bold uppercase">{ticket.status}</span>
                                        {expandedId === ticket.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                    </div>
                                </div>

                                {expandedId === ticket.id && (
                                    <div className="mt-4 pt-4 border-t border-gray-200 animate-fade-in text-sm">
                                        <p className="text-gray-700 mb-4">{ticket.description}</p>

                                        {/* Live Tracking Stepper */}
                                        <div className="relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-indigo-300 before:to-transparent pt-2">
                                            {["Received", "Assigned", "On Site", "Resolved"].map((stepText, idx) => {
                                                const stepNum = idx + 1;
                                                const isActive = getStatusStep(ticket.status) >= stepNum;
                                                return (
                                                    <div key={stepText} className={`relative flex items-center justify-between mb-4 group ${isActive ? 'opacity-100' : 'opacity-40 grayscale'} transition-all`}>
                                                        <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 border-white text-white shadow shrink-0 z-10 ${isActive ? 'bg-indigo-500' : 'bg-gray-300'}`}>
                                                            {isActive && stepNum < getStatusStep(ticket.status) ? "✓" : stepNum}
                                                        </div>
                                                        <div className="w-[calc(100%-3rem)] bg-white p-3 rounded border shadow-sm">
                                                            <div className="font-bold text-slate-800">{stepText}</div>
                                                        </div>
                                                    </div>
                                                )
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CitizenPortal;
