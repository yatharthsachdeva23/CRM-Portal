import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, ChevronDown, ChevronUp, MapPin, Tag } from 'lucide-react';
import { updateTicketStatus } from '../services/api';

const TicketCard = ({ ticket, refreshTickets }) => {
    const [timeLeft, setTimeLeft] = useState(0);
    const [expanded, setExpanded] = useState(false);
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        // Calculate SLA diff
        const calculateTimeLeft = () => {
            const slaTime = new Date(ticket.sla_deadline).getTime();
            const now = new Date().getTime();
            return Math.floor((slaTime - now) / 1000);
        };

        setTimeLeft(calculateTimeLeft());
        const interval = setInterval(() => setTimeLeft(calculateTimeLeft()), 1000);
        return () => clearInterval(interval);
    }, [ticket.sla_deadline]);

    const isEscalated = timeLeft <= 0 && ticket.status !== 'Resolved';
    const isWarning = timeLeft > 0 && timeLeft < 3600 && ticket.status !== 'Resolved'; // Under 1 hr

    const formatTime = (seconds) => {
        if (seconds <= 0) return "ESCALATED";
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h > 0 ? h + 'h ' : ''}${m}m ${s}s`;
    };

    const handleStatusChange = async (e, newStatus) => {
        e.stopPropagation();
        setUpdating(true);
        try {
            await updateTicketStatus(ticket.id, newStatus);
            refreshTickets();
        } catch (err) {
            alert("Failed to update status");
        } finally {
            setUpdating(false);
        }
    };

    return (
        <div
            onClick={() => setExpanded(!expanded)}
            className={`p-4 rounded-lg border-l-4 shadow-sm mb-3 transition-colors duration-300 cursor-pointer hover:shadow-md ${ticket.status === 'Resolved'
                    ? 'bg-gray-50 border-gray-400 opacity-70'
                    : isEscalated
                        ? 'bg-red-50 border-red-500 animate-pulse'
                        : isWarning
                            ? 'bg-yellow-50 border-yellow-500'
                            : 'bg-white border-indigo-500'
                }`}>
            <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-bold text-gray-500">#{ticket.id} - <span className="text-indigo-600">{ticket.source}</span></span>

                {ticket.status !== 'Resolved' && (
                    <span className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded ${isEscalated ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
                        }`}>
                        {isEscalated ? <AlertTriangle size={12} /> : <Clock size={12} />}
                        {formatTime(timeLeft)}
                    </span>
                )}
            </div>

            <div className="flex justify-between items-center">
                <h4 className="font-bold text-gray-800 flex items-center gap-2">
                    {ticket.category}
                    {ticket.sentiment_score > 0.7 && <span className="bg-red-100 text-red-700 text-[10px] px-1 py-0.5 rounded">URGENT</span>}
                </h4>
                {expanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
            </div>

            {isEscalated && (
                <div className="mt-2 text-xs font-semibold text-red-600 bg-red-100 px-2 py-1 rounded inline-block">
                    Auto-Escalated to Supervisor
                </div>
            )}

            {/* Expanded Details */}
            {expanded && (
                <div className="mt-4 pt-3 border-t border-gray-100 animate-fade-in text-sm">
                    <p className="text-gray-700 italic mb-3">"{ticket.description}"</p>

                    <div className="space-y-1 mb-4">
                        <p className="text-xs text-gray-500 flex items-center gap-1"><MapPin size={12} /> {ticket.lat?.toFixed(4)}, {ticket.lon?.toFixed(4)}</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1"><Tag size={12} /> {ticket.sub_category || "General Issue"}</p>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-wrap gap-2 mt-2">
                        {ticket.status === 'Received' && (
                            <button disabled={updating} onClick={(e) => handleStatusChange(e, 'Assigned')} className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold py-1.5 px-3 rounded shadow">
                                Assign Team
                            </button>
                        )}
                        {ticket.status === 'Assigned' && (
                            <button disabled={updating} onClick={(e) => handleStatusChange(e, 'On Site')} className="bg-orange-500 hover:bg-orange-600 text-white text-xs font-bold py-1.5 px-3 rounded shadow">
                                Mark On-Site
                            </button>
                        )}
                        {ticket.status === 'On Site' && (
                            <button disabled={updating} onClick={(e) => handleStatusChange(e, 'Resolved')} className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-1.5 px-3 rounded shadow">
                                Resolve Ticket
                            </button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

const KanbanBoard = ({ tickets = [], refreshTickets }) => {
    return (
        <div className="flex flex-col lg:flex-row h-full gap-4 overflow-x-auto">

            {/* Received Column */}
            <div className="bg-gray-100 rounded-lg p-3 flex-1 min-w-[300px]">
                <h3 className="text-sm font-bold text-gray-500 uppercase mb-3 flex justify-between items-center">
                    Received
                    <span className="bg-gray-300 text-gray-700 px-2 rounded-full text-xs">{tickets.filter(t => t.status === 'Received').length}</span>
                </h3>
                {tickets.filter(t => t.status === 'Received').map(t => (
                    <TicketCard key={t.id} ticket={t} refreshTickets={refreshTickets} />
                ))}
            </div>

            {/* Assigned Column */}
            <div className="bg-gray-100 rounded-lg p-3 flex-1 min-w-[300px]">
                <h3 className="text-sm font-bold text-gray-500 uppercase mb-3 flex justify-between items-center">
                    Assigned
                    <span className="bg-gray-300 text-gray-700 px-2 rounded-full text-xs">{tickets.filter(t => t.status === 'Assigned').length}</span>
                </h3>
                {tickets.filter(t => t.status === 'Assigned').map(t => (
                    <TicketCard key={t.id} ticket={t} refreshTickets={refreshTickets} />
                ))}
            </div>

            {/* On Site Column */}
            <div className="bg-gray-100 rounded-lg p-3 flex-1 min-w-[300px]">
                <h3 className="text-sm font-bold text-gray-500 uppercase mb-3 flex justify-between items-center">
                    On Site
                    <span className="bg-gray-300 text-gray-700 px-2 rounded-full text-xs">{tickets.filter(t => t.status === 'On Site').length}</span>
                </h3>
                {tickets.filter(t => t.status === 'On Site').map(t => (
                    <TicketCard key={t.id} ticket={t} refreshTickets={refreshTickets} />
                ))}
            </div>

        </div>
    );
};

export default KanbanBoard;
