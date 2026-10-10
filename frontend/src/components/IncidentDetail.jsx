import { useState, useEffect } from "react";
import { ArrowLeft, Clock, CheckCircle2, AlertCircle, RefreshCw, AlertTriangle } from "lucide-react";
import Timeline from "./Timeline";
import AgentPanel from "./AgentPanel";
import { api, getBaseUrl } from "../services/api";

export default function IncidentDetail({ incident: initialIncident, onBack }) {
  const [incident, setIncident] = useState(initialIncident);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refreshIncident = async () => {
    if (!initialIncident?.id) return;
    setLoading(true);
    setError(null);
    try {
      const freshData = await api.getIncident(initialIncident.id);
      setIncident(freshData);
    } catch (err) {
      setError(err.message || "Failed to load incident details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setIncident(initialIncident);
    refreshIncident();
  }, [initialIncident?.id]);

  if (!incident) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case "Investigating":
        return "bg-amber-100 text-amber-700 border-amber-200";
      case "Resolved":
        return "bg-emerald-100 text-emerald-700 border-emerald-200";
      case "Failed":
        return "bg-rose-100 text-rose-700 border-rose-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "Investigating":
        return <Clock size={16} className="mr-1.5" />;
      case "Resolved":
        return <CheckCircle2 size={16} className="mr-1.5" />;
      case "Failed":
        return <AlertCircle size={16} className="mr-1.5" />;
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full w-full">
      {/* Top Header */}
      <div className="bg-white border-b border-slate-200 px-8 py-5 flex items-center justify-between shadow-sm sticky top-0 z-10">
        <div className="flex items-center gap-6">
          <button
            onClick={onBack}
            className="p-2 -ml-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft size={20} />
          </button>

          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">{incident.id}</h1>
              <span
                className={`flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${getStatusColor(
                  incident.status
                )}`}
              >
                {getStatusIcon(incident.status)}
                {incident.status === "Investigating" && (
                  <span className="relative flex h-2.5 w-2.5 mr-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
                  </span>
                )}
                {incident.status}
              </span>
            </div>
            <p className="text-slate-500 mt-1">{incident.summary}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={refreshIncident}
            disabled={loading}
            className="p-2 text-slate-500 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
            title="Refresh Incident Details"
          >
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          </button>
          <div className="text-right">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Facility</p>
            <p className="text-sm font-semibold text-slate-900">{incident.facility}</p>
          </div>
          <div className="w-px h-8 bg-slate-200 self-center"></div>
          <div className="text-right">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Stream</p>
            <p className="text-sm font-semibold text-slate-900">{incident.wasteStream}</p>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-rose-50 border-b border-rose-200 px-8 py-3 text-xs text-rose-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} />
            <span>{error}</span>
          </div>
          <button onClick={refreshIncident} className="underline font-semibold">Retry</button>
        </div>
      )}

      {/* Two-Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column: Timeline */}
        <div className="w-3/5 overflow-y-auto p-8 border-r border-slate-200 bg-slate-50 flex flex-col gap-8">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-6 flex items-center gap-2">
              Evidence Timeline
            </h2>
            <Timeline events={incident.timeline || []} />
          </div>
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-md font-semibold text-slate-900 mb-4">Additional Evidence</h3>
            {incident.uploadedEvidence && incident.uploadedEvidence.length > 0 && (
              <ul className="mb-4 space-y-2">
                {incident.uploadedEvidence.map(ev => (
                  <li key={ev.id} className="flex items-center justify-between p-3 bg-slate-50 rounded border border-slate-100">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-slate-700">{ev.filename}</span>
                      <span className="text-xs text-slate-400">({Math.round(ev.sizeBytes / 1024)} KB)</span>
                    </div>
                    <a 
                      href={`${getBaseUrl()}${ev.storagePath}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-theme-6-light hover:underline font-medium"
                    >
                      View
                    </a>
                  </li>
                ))}
              </ul>
            )}
            
            <div className="flex items-center gap-3">
              <input 
                type="file" 
                id="evidence-upload"
                className="hidden"
                accept=".jpg,.jpeg,.png,.webp,.pdf"
                onChange={async (e) => {
                  const file = e.target.files[0];
                  if (!file) return;
                  setLoading(true);
                  setError(null);
                  try {
                    await api.uploadEvidence(incident.id, file);
                    await refreshIncident();
                  } catch (err) {
                    setError(err.message || "Failed to upload evidence.");
                    setLoading(false);
                  }
                }}
              />
              <label 
                htmlFor="evidence-upload"
                className={`px-4 py-2 rounded-lg font-medium text-sm border transition-colors cursor-pointer ${
                  loading 
                    ? "bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                }`}
              >
                {loading ? "Uploading..." : "Upload File"}
              </label>
              <span className="text-xs text-slate-500">Max 5MB (JPG, PNG, WebP, PDF)</span>
            </div>
          </div>
        </div>

        {/* Right Column: Agent Panel */}
        <div className="w-2/5 overflow-y-auto bg-white">
          <AgentPanel incident={incident} onUpdateIncident={(updated) => setIncident(updated)} />
        </div>
      </div>
    </div>
  );
}
