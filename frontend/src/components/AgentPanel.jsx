import { Bot, Sparkles, AlertCircle, Check, X, ShieldAlert, FileSearch } from "lucide-react";

export default function AgentPanel({ incident }) {
  const isActionRequired = incident.agentActionRequired;

  return (
    <div className="h-full flex flex-col bg-slate-50 border-l border-indigo-100">
      {/* Header */}
      <div className="bg-white p-6 border-b border-indigo-100 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500"></div>
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-indigo-100 rounded-lg text-indigo-700">
            <Bot size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              LoopBack AI <Sparkles size={16} className="text-amber-500" />
            </h2>
            <p className="text-sm text-slate-500">Investigation Assistant</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-y-auto">

        {/* Current Status Log */}
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">System Log</h3>

          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="mt-0.5"><FileSearch size={16} className="text-slate-400" /></div>
              <div>
                <p className="text-sm text-slate-700">Analyzed MRF intake logs.</p>
                <p className="text-xs text-slate-400 mt-0.5">10:31 AM</p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="mt-0.5"><ShieldAlert size={16} className="text-rose-500" /></div>
              <div>
                <p className="text-sm text-slate-700 font-medium">Detected discrepancy: Weight mismatch between source and destination.</p>
                <p className="text-xs text-slate-400 mt-0.5">10:32 AM</p>
              </div>
            </div>

            {/* Pulsing current status */}
            <div className="flex gap-3 bg-white p-3 rounded-lg border border-indigo-100 shadow-sm">
              <div className="mt-0.5 relative flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-indigo-500"></span>
              </div>
              <div>
                <p className="text-sm font-medium text-indigo-900">{incident.agentStatus}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Card */}
        {isActionRequired && (
          <div className="bg-white rounded-xl border-2 border-indigo-200 shadow-md overflow-hidden relative">
            <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
            <div className="p-5">
              <div className="flex items-center gap-2 text-indigo-700 font-bold mb-3">
                <AlertCircle size={20} />
                Action Required
              </div>

              <h4 className="font-semibold text-slate-900 mb-2">Request Missing Documentation</h4>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                The destination facility flagged the load for contamination, but the required photographic evidence from the scalehouse is blurry. I need approval to automatically email the vendor requesting a clearer photo.
              </p>

              <div className="space-y-3">
                <button className="w-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors shadow-sm">
                  <Check size={18} />
                  Approve Request for Missing Photo
                </button>
                <button className="w-full bg-white hover:bg-slate-50 active:bg-slate-100 text-slate-700 border border-slate-300 font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors">
                  <X size={18} />
                  Override / Reject
                </button>
              </div>
            </div>
          </div>
        )}

        {!isActionRequired && incident.status !== 'Resolved' && (
           <div className="bg-slate-100 rounded-xl border border-slate-200 p-6 text-center">
             <Bot size={32} className="mx-auto text-slate-400 mb-3" />
             <p className="text-slate-600 font-medium">AI is currently investigating.</p>
             <p className="text-sm text-slate-500 mt-1">No human intervention required at this time.</p>
           </div>
        )}
      </div>
    </div>
  );
}
