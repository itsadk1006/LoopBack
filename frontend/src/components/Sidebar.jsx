import { LayoutDashboard, History, Settings, Recycle } from "lucide-react";

export default function Sidebar({ currentView, setCurrentView }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "history", label: "History", icon: History },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col h-screen sticky top-0">
      <div className="h-16 flex items-center px-6 border-b border-slate-800 text-white font-bold text-xl gap-2">
        <Recycle className="text-emerald-400" />
        LoopBack
      </div>

      <nav className="flex-1 py-6 px-3 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentView(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-200 ${
              currentView === item.id || (currentView === 'detail' && item.id === 'dashboard')
                ? "bg-indigo-600 text-white"
                : "hover:bg-slate-800 hover:text-white"
            }`}
          >
            <item.icon size={20} />
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold text-sm">
            JD
          </div>
          <div className="text-sm">
            <p className="text-white font-medium">Jane Doe</p>
            <p className="text-slate-500 text-xs">Supervisor</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
