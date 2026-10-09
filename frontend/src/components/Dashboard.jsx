import { useState } from "react";
import { Search, AlertCircle, CheckCircle2, Clock, Factory } from "lucide-react";
import { incidents } from "../data";

export default function Dashboard({ onSelectIncident }) {
  const [filter, setFilter] = useState("All");

  const filteredIncidents = incidents.filter(inc => {
    if (filter === "All") return true;
    if (filter === "Awaiting AI" && inc.status === "Investigating" && !inc.agentActionRequired) return true;
    if (filter === "Awaiting Human Approval" && inc.agentActionRequired) return true;
    return false;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case "Investigating": return "bg-amber-100 text-amber-700 border-amber-200";
      case "Resolved": return "bg-emerald-100 text-emerald-700 border-emerald-200";
      case "Failed": return "bg-rose-100 text-rose-700 border-rose-200";
      default: return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "Investigating": return <Clock size={14} className="mr-1" />;
      case "Resolved": return <CheckCircle2 size={14} className="mr-1" />;
      case "Failed": return <AlertCircle size={14} className="mr-1" />;
      default: return null;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto w-full">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Incident Inbox</h1>
          <p className="text-slate-500 mt-1">Manage and track recycling failures across facilities.</p>
        </div>
        <div className="flex gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              type="text"
              placeholder="Search incidents..."
              className="pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-64"
            />
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-6 border-b border-slate-200 pb-4">
        {["All", "Awaiting AI", "Awaiting Human Approval"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f
                ? "bg-slate-900 text-white"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredIncidents.map((incident) => (
          <div
            key={incident.id}
            onClick={() => onSelectIncident(incident)}
            className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 cursor-pointer hover:shadow-md hover:border-slate-300 transition-all duration-200 flex flex-col group"
          >
            <div className="flex justify-between items-start mb-4">
              <span className="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                {incident.id}
              </span>
              <span className={`flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusColor(incident.status)}`}>
                {getStatusIcon(incident.status)}
                {incident.status === 'Investigating' && (
                  <span className="relative flex h-2 w-2 mr-1">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                  </span>
                )}
                {incident.status}
              </span>
            </div>

            <h3 className="text-lg font-medium text-slate-800 mb-1 leading-snug line-clamp-2">
              {incident.summary}
            </h3>

            <div className="mt-auto pt-4 flex items-center justify-between text-sm text-slate-500">
              <div className="flex items-center gap-1.5">
                <Factory size={16} />
                <span className="truncate max-w-[120px]">{incident.facility}</span>
              </div>
              <div className="font-medium bg-slate-100 px-2 py-1 rounded-md">
                {incident.wasteStream}
              </div>
            </div>

            {incident.agentActionRequired && (
              <div className="mt-3 bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs py-1.5 px-2 rounded-md font-medium flex items-center gap-1.5">
                <AlertCircle size={14} />
                Human approval required
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
