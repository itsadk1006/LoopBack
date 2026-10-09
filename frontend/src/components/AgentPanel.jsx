import { useState } from "react";
import {
  Bot,
  Sparkles,
  AlertCircle,
  Check,
  X,
  ShieldAlert,
  RotateCw,
  HelpCircle,
  CheckCircle,
  Clock,
  Ban,
  UserCheck,
  FileQuestion
} from "lucide-react";
import { api } from "../services/api";

export default function AgentPanel({ incident, onUpdateIncident }) {
  const [investigating, setInvestigating] = useState(false);
  const [submittingAction, setSubmittingAction] = useState(false);
  const [error, setError] = useState(null);

  const proposedAction = incident.proposedAction;
  const investigation = incident.investigation;

  const handleRunInvestigation = async () => {
    setInvestigating(true);
    setError(null);
    try {
      const updated = await api.investigateIncident(incident.id);
      if (onUpdateIncident) onUpdateIncident(updated);
    } catch (err) {
      setError(err.message || "Investigation failed.");
    } finally {
      setInvestigating(false);
    }
  };

  const handleAction = async (actionType) => {
    setSubmittingAction(true);
    setError(null);
    try {
      const updated = await api.performAction(incident.id, actionType);
      if (onUpdateIncident) onUpdateIncident(updated);
    } catch (err) {
      setError(err.message || `Failed to ${actionType} action.`);
    } finally {
      setSubmittingAction(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-50 border-l border-indigo-100">
      {/* Top Header */}
      <div className="bg-white p-6 border-b border-indigo-100 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500"></div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
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

          <button
            onClick={handleRunInvestigation}
            disabled={investigating}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-semibold transition-colors shadow-sm disabled:opacity-50"
          >
            <RotateCw size={14} className={investigating ? "animate-spin" : ""} />
            {investigating ? "Investigating..." : "Re-Run Investigation"}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-3 rounded-lg flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* System Log / Live Status */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">System Log</h3>

          <div className="space-y-3">
            <div className="flex gap-3 bg-white p-3 rounded-lg border border-indigo-100 shadow-sm">
              <div className="mt-0.5 relative flex h-4 w-4 shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-indigo-500"></span>
              </div>
              <div>
                <p className="text-sm font-medium text-indigo-900">{incident.agentStatus}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Proposed Action Card */}
        {proposedAction && (
          <div className="bg-white rounded-xl border-2 border-indigo-200 shadow-md overflow-hidden relative">
            <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
            <div className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm">
                  <AlertCircle size={18} />
                  Proposed Action
                </div>

                {/* Status Badge */}
                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded-full border flex items-center gap-1 ${
                    proposedAction.status === "approved"
                      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                      : proposedAction.status === "rejected"
                      ? "bg-rose-50 text-rose-700 border-rose-200"
                      : "bg-amber-50 text-amber-700 border-amber-200"
                  }`}
                >
                  {proposedAction.status === "approved" && <Check size={12} />}
                  {proposedAction.status === "rejected" && <Ban size={12} />}
                  {proposedAction.status === "pending" && <Clock size={12} />}
                  <span className="capitalize">{proposedAction.status}</span>
                </span>
              </div>

              <h4 className="font-semibold text-slate-900 text-base mb-2">{proposedAction.title}</h4>
              <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                {proposedAction.description}
              </p>

              {proposedAction.targetParty && (
                <p className="text-xs text-slate-500 mb-4 font-medium">
                  Target Responsible Party: <span className="text-slate-800 font-semibold">{proposedAction.targetParty}</span>
                </p>
              )}

              {/* Action Buttons if status is pending */}
              {proposedAction.status === "pending" ? (
                <div className="space-y-3">
                  <button
                    onClick={() => handleAction("approve")}
                    disabled={submittingAction}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors shadow-sm disabled:opacity-50 text-sm"
                  >
                    <Check size={18} />
                    {submittingAction ? "Processing..." : `Approve Action`}
                  </button>
                  <button
                    onClick={() => handleAction("reject")}
                    disabled={submittingAction}
                    className="w-full bg-white hover:bg-slate-50 active:bg-slate-100 text-slate-700 border border-slate-300 font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 text-sm"
                  >
                    <X size={18} />
                    {submittingAction ? "Processing..." : "Override / Reject Action"}
                  </button>
                </div>
              ) : (
                /* Clear Explanation for Approved/Rejected Status */
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs space-y-2">
                  <div className="flex items-center justify-between font-semibold text-slate-800 border-b border-slate-200 pb-2">
                    <span className="flex items-center gap-1.5 text-slate-700">
                      <UserCheck size={14} className="text-indigo-600" />
                      Decision Recorded
                    </span>
                    <span className={`capitalize font-bold ${proposedAction.status === 'approved' ? 'text-emerald-700' : 'text-rose-700'}`}>
                      {proposedAction.status}
                    </span>
                  </div>
                  <div className="text-slate-600 space-y-1">
                    <p><span className="font-semibold text-slate-700">Decided by:</span> {proposedAction.decidedBy || "Human Operator"}</p>
                    {proposedAction.decidedAt && (
                      <p><span className="font-semibold text-slate-700">Time:</span> {new Date(proposedAction.decidedAt).toLocaleString()}</p>
                    )}
                    <p><span className="font-semibold text-slate-700">Notes/Reason:</span> {proposedAction.notes || "Recorded in immutable audit timeline."}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Structured Investigation Findings */}
        {investigation && (
          <div className="space-y-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Investigation Findings</h3>

            {/* Verified Facts */}
            {investigation.verifiedFacts?.length > 0 && (
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <CheckCircle size={14} className="text-emerald-500" />
                  Verified Facts (From Source Logs)
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-600 pl-4 list-disc">
                  {investigation.verifiedFacts.map((fact, i) => (
                    <li key={i}>{fact}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Hypotheses */}
            {investigation.hypotheses?.length > 0 && (
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h4 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <HelpCircle size={14} className="text-amber-500" />
                  Plausible Hypotheses (AI Inferred)
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-600 pl-4 list-disc">
                  {investigation.hypotheses.map((hyp, i) => (
                    <li key={i}>{hyp}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actionable Missing Evidence / Information Gaps */}
            {investigation.missingEvidence?.length > 0 && (
              <div className="bg-amber-50/60 p-4 rounded-xl border border-amber-200 shadow-sm">
                <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <ShieldAlert size={14} className="text-amber-600" />
                  Actionable Evidence Gaps (Not Yet Retrieved)
                </h4>
                <div className="space-y-2 text-xs">
                  {investigation.missingEvidence.map((gap, i) => (
                    <div key={i} className="bg-white p-2.5 rounded-lg border border-amber-200/80 flex items-start gap-2">
                      <FileQuestion size={16} className="text-amber-600 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-semibold text-slate-800">{gap}</p>
                        <p className="text-amber-700 text-[11px] mt-0.5 font-medium">
                          Status: Record missing. Action required to retrieve and resolve uncertainty.
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendation */}
            {investigation.recommendation && (
              <div className="bg-indigo-50/60 p-4 rounded-xl border border-indigo-200 text-xs">
                <span className="font-bold text-indigo-900 block mb-1">AI Recommendation:</span>
                <p className="text-indigo-800 leading-relaxed">{investigation.recommendation}</p>
              </div>
            )}
          </div>
        )}

        {!proposedAction && incident.status !== "Resolved" && (
          <div className="bg-slate-100 rounded-xl border border-slate-200 p-6 text-center">
            <Bot size={32} className="mx-auto text-slate-400 mb-3" />
            <p className="text-slate-600 font-medium">AI investigation in progress.</p>
            <p className="text-xs text-slate-500 mt-1">No human intervention required at this time.</p>
          </div>
        )}
      </div>
    </div>
  );
}
