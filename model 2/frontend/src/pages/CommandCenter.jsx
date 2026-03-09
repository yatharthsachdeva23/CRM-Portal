import React, { useState, useEffect } from 'react';
import LiveMap from '../components/LiveMap';
import KanbanBoard from '../components/KanbanBoard';
import { fetchAllTickets } from '../services/api';
import { Sparkles, RefreshCw } from 'lucide-react';

const CommandCenter = () => {
    const [tickets, setTickets] = useState([]);
    const [showPredictive, setShowPredictive] = useState(false);
    const [loading, setLoading] = useState(true);

    const loadTickets = async () => {
        try {
            const { data } = await fetchAllTickets();
            setTickets(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTickets();
        const interval = setInterval(loadTickets, 5000); // 5 sec live refresh
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="h-full flex flex-col gap-6 animate-fade-in pb-10">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center text-gray-800 gap-4">
                <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-500 flex items-center gap-2">
                        Emergency Command Center
                        {loading && <RefreshCw className="animate-spin text-gray-400" size={20} />}
                    </h2>
                    <p className="text-sm font-medium text-gray-500">AI-Powered Infrastructure Routing (Delhi Metro Region)</p>
                </div>

                <div className="flex gap-4 items-center">
                    <button
                        onClick={() => setShowPredictive(!showPredictive)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold shadow transition-all ${showPredictive ? 'bg-purple-600 text-white animate-pulse' : 'bg-white text-purple-600 outline outline-2 outline-purple-200 hover:bg-purple-50'}`}>
                        <Sparkles size={18} /> {showPredictive ? "Predictive Insights ON" : "Analyze Red Zones"}
                    </button>

                    <div className="bg-white px-4 py-2 rounded-lg shadow font-medium border-l-4 border-emerald-500">
                        <span className="text-emerald-600">Electricity SLA: 98%</span>
                    </div>
                    <div className="bg-white px-4 py-2 rounded-lg shadow font-medium border-l-4 border-orange-500">
                        <span className="text-orange-600">Water SLA: 85%</span>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[600px]">
                <div className="lg:col-span-2 bg-white rounded-xl shadow-md overflow-hidden flex flex-col border border-gray-100 relative">
                    <div className="p-4 border-b bg-gray-50 font-semibold text-gray-700 flex justify-between">
                        Live GIS & Heatmap {showPredictive && <span className="text-purple-600 animate-pulse text-xs">AI Overlay Enabled</span>}
                    </div>
                    <div className="flex-1 w-full relative z-0 h-[500px] lg:h-auto">
                        <LiveMap tickets={tickets} showPredictive={showPredictive} />
                    </div>
                </div>

                <div className="bg-white rounded-xl shadow-md overflow-hidden flex flex-col border border-gray-100">
                    <div className="p-4 border-b bg-gray-50 font-semibold text-gray-700">Smart Kanban / Escalations</div>
                    <div className="flex-1 overflow-y-auto p-4 bg-slate-50">
                        <KanbanBoard tickets={tickets} refreshTickets={loadTickets} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CommandCenter;
