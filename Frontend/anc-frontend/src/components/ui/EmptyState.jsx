export default function EmptyState({ icon, title, sub, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="text-5xl mb-4 opacity-30">{icon}</div>
      <p className="font-display text-lg font-semibold text-slate-300">{title}</p>
      {sub && <p className="text-sm text-slate-500 mt-1">{sub}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
