import { useState } from "react";
import { ClipboardList, Truck, Factory, AlertTriangle, CheckCircle, XCircle, Calendar, Image as ImageIcon, FileText } from "lucide-react";

export default function Timeline({ events }) {
  const [expandedEvent, setExpandedEvent] = useState(null);

  const getIcon = (iconName, type) => {
    let iconClass = "text-slate-500";
    let bgClass = "bg-slate-100 border-slate-300";

    if (type === "flagged") {
      iconClass = "text-rose-600";
      bgClass = "bg-rose-100 border-rose-300";
    } else if (type === "success") {
      iconClass = "text-emerald-600";
      bgClass = "bg-emerald-100 border-emerald-300";
    } else if (type === "failed") {
      iconClass = "text-rose-600";
      bgClass = "bg-rose-100 border-rose-300";
    }

    const iconProps = { size: 20, className: iconClass };
    let IconComponent;

    switch (iconName) {
      case "clipboard": IconComponent = <ClipboardList {...iconProps} />; break;
      case "truck": IconComponent = <Truck {...iconProps} />; break;
      case "factory": IconComponent = <Factory {...iconProps} />; break;
      case "alert-triangle": IconComponent = <AlertTriangle {...iconProps} />; break;
      case "check-circle": IconComponent = <CheckCircle {...iconProps} />; break;
      case "x-circle": IconComponent = <XCircle {...iconProps} />; break;
      case "calendar": IconComponent = <Calendar {...iconProps} />; break;
      default: IconComponent = <div className={`w-5 h-5 rounded-full ${iconClass.replace('text-', 'bg-')}`}></div>;
    }

    return (
      <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center z-10 relative ${bgClass}`}>
        {IconComponent}
      </div>
    );
  };

  const toggleExpand = (id) => {
    setExpandedEvent(expandedEvent === id ? null : id);
  };

  return (
    <div className="relative pl-4">
      {/* Continuous vertical line */}
      <div className="absolute left-9 top-4 bottom-4 w-0.5 bg-slate-200 z-0"></div>

      <div className="space-y-8 relative z-10">
        {events.map((event) => {
          const isExpanded = expandedEvent === event.id;
          const hasEvidence = !!event.evidence;

          return (
            <div key={event.id} className="flex gap-6">
              <div className="flex flex-col items-center">
                {getIcon(event.icon, event.type)}
              </div>

              <div className="flex-1 pb-2">
                <div
                  className={`bg-white p-5 rounded-xl border shadow-sm transition-all duration-200 ${
                    hasEvidence ? 'cursor-pointer hover:shadow-md hover:border-indigo-300' : 'border-slate-200'
                  } ${event.type === 'flagged' ? 'border-rose-200 shadow-rose-100/50' : ''}`}
                  onClick={() => hasEvidence && toggleExpand(event.id)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className={`font-semibold text-lg ${event.type === 'flagged' ? 'text-rose-700' : 'text-slate-900'}`}>
                      {event.title}
                    </h3>
                    <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
                      {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <p className="text-slate-600 mb-3">{event.description}</p>

                  {hasEvidence && (
                    <div className="mt-2">
                      <div className="inline-flex items-center gap-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg">
                        {event.evidence.type === 'photo' ? <ImageIcon size={16} /> : <FileText size={16} />}
                        View Evidence Attached
                      </div>

                      {isExpanded && (
                        <div className="mt-4 pt-4 border-t border-slate-100 animate-in fade-in slide-in-from-top-2 duration-200">
                          {event.evidence.type === 'photo' ? (
                            <div className="rounded-lg overflow-hidden border border-slate-200 bg-slate-50 relative group">
                              <img
                                src={event.evidence.url}
                                alt="Evidence"
                                className="w-full h-48 object-cover"
                              />
                              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <button className="bg-white text-slate-900 px-4 py-2 rounded-lg font-medium text-sm shadow-lg">
                                  View Full Size
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div className="p-2 bg-white rounded shadow-sm border border-slate-200">
                                  <FileText className="text-slate-500" size={24} />
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-slate-900">Delivery_Receipt_#4892.pdf</p>
                                  <p className="text-xs text-slate-500">1.2 MB</p>
                                </div>
                              </div>
                              <button className="text-indigo-600 hover:text-indigo-700 text-sm font-medium px-3 py-1.5 hover:bg-indigo-50 rounded-md transition-colors">
                                Download
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
