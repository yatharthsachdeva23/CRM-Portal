import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  PlusCircle, 
  Search, 
  MapPin, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  TrendingUp,
  MessageSquare
} from 'lucide-react';

const CitizenDashboard: React.FC = () => {
  const { user } = useAuth();
  const [complaintText, setComplaintText] = useState('');
  
  const myTickets = [
    { id: 'TKT-101', title: 'Street light broken', status: 'In Progress', date: '2024-03-24' },
    { id: 'TKT-098', title: 'Garbage dump in park', status: 'Resolved', date: '2024-03-20' },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome & Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="md:col-span-2 bg-gradient-to-br from-blue-600/20 to-purple-600/20 border-blue-500/30">
          <CardHeader>
            <CardTitle className="text-xl">Welcome back, {user?.username}!</CardTitle>
            <p className="text-slate-300 text-sm">You have helped solve 12 community issues.</p>
          </CardHeader>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              Trust Score
            </CardTitle>
            <p className="text-2xl font-bold text-white">850</p>
          </CardHeader>
        </Card>
      </div>

      {/* Quick Submit */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <PlusCircle className="w-5 h-5 text-blue-400" />
            Submit New Complaint
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            <Input 
              placeholder="Describe the issue (e.g., Pothole near Sector 4)" 
              className="bg-slate-950 border-slate-800"
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
            />
            <div className="flex gap-2">
              <Button className="bg-blue-600 hover:bg-blue-500 flex-1">
                <PlusCircle className="w-4 h-4 mr-2" /> Submit
              </Button>
              <Button variant="outline" className="border-slate-800">
                <MapPin className="w-4 h-4 mr-2" /> Add Location
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* My Tickets */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Clock className="w-5 h-5 text-purple-400" />
          My Recent Tickets
        </h3>
        <div className="grid grid-cols-1 gap-4">
          {myTickets.map(ticket => (
            <Card key={ticket.id} className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-colors">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-start gap-4">
                  <div className={`mt-1 p-2 rounded-lg ${ticket.status === 'Resolved' ? 'bg-green-500/10' : 'bg-blue-500/10'}`}>
                    {ticket.status === 'Resolved' ? <CheckCircle2 className="w-5 h-5 text-green-400" /> : <AlertCircle className="w-5 h-5 text-blue-400" />}
                  </div>
                  <div>
                    <h4 className="font-medium text-white">{ticket.title}</h4>
                    <p className="text-xs text-slate-400">{ticket.id} • Submitted on {ticket.date}</p>
                  </div>
                </div>
                <Badge variant={ticket.status === 'Resolved' ? 'default' : 'outline'} className={ticket.status === 'Resolved' ? 'bg-green-600' : 'border-blue-500 text-blue-400'}>
                  {ticket.status}
                </Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Public Trust Leaderboard */}
      <Card className="bg-slate-900 border-slate-800 overflow-hidden">
        <CardHeader className="bg-slate-800/50">
          <CardTitle className="text-sm font-bold flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Community Leaderboard
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-slate-800">
            {[1, 2, 3].map(i => (
              <div key={i} className="px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-slate-500 font-mono">#{i}</span>
                  <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold">
                    {['UP', 'JD', 'AS'][i-1]}
                  </div>
                  <span className="text-sm">User_{i}234</span>
                </div>
                <span className="text-sm font-bold text-blue-400">{1000 - i*50} pts</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CitizenDashboard;
