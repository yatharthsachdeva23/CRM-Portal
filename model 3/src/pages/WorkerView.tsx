import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Camera, 
  MapPin, 
  Navigation, 
  CheckCircle2, 
  AlertTriangle,
  Clock,
  Briefcase
} from 'lucide-react';

const WorkerView: React.FC = () => {
  const [activeTasks, setActiveTasks] = useState([
    { id: 'M-1002', title: 'Road Repair', location: 'Sector 15, Near Metro', priority: 'High', deadline: '2h remaining' },
    { id: 'M-1005', title: 'Water Leakage', location: 'A-Block Park', priority: 'Medium', deadline: '5h remaining' },
  ]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Briefcase className="w-6 h-6 text-orange-400" />
          Field Assignments
        </h2>
        <Badge variant="outline" className="text-orange-400 border-orange-400/30">
          2 Pending
        </Badge>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {activeTasks.map(task => (
          <Card key={task.id} className="bg-slate-900 border-slate-800 overflow-hidden">
            <CardHeader className="pb-3 border-b border-slate-800/50 bg-slate-800/20">
              <div className="flex justify-between items-start">
                <div>
                  <Badge className={task.priority === 'High' ? 'bg-red-600' : 'bg-orange-600'}>
                    {task.priority} Priority
                  </Badge>
                  <CardTitle className="text-lg mt-2">{task.title}</CardTitle>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 font-mono">{task.id}</p>
                  <p className="text-xs text-orange-400 font-medium flex items-center justify-end gap-1 mt-1">
                    <Clock className="w-3 h-3" /> {task.deadline}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <MapPin className="w-4 h-4 text-slate-400" />
                {task.location}
              </div>
              <div className="aspect-video bg-slate-950 rounded-lg border border-slate-800 flex items-center justify-center text-slate-600 italic text-sm">
                Map Preview / Route
              </div>
            </CardContent>
            <CardFooter className="p-2 bg-slate-800/30 flex gap-2">
              <Button className="flex-1 bg-blue-600 hover:bg-blue-500">
                <Navigation className="w-4 h-4 mr-2" /> Navigate
              </Button>
              <Button className="flex-1 bg-green-600 hover:bg-green-500">
                <Camera className="w-4 h-4 mr-2" /> Resolve
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* Resolution Instructions */}
      <Card className="bg-slate-900/50 border-slate-800 border-dashed">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
            <div className="text-xs text-slate-300 space-y-1">
              <p className="text-slate-100 font-medium">Compliance Note:</p>
              <p>• Only live camera photos allowed (no gallery access).</p>
              <p>• GPS and Timestamp will be automatically tagged.</p>
              <p>• Data will be verified against the original complaint image.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WorkerView;
