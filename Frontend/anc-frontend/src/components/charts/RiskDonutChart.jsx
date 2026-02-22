import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = { 
  CRITICAL: '#ef4444', 
  HIGH: '#f97316', 
  MEDIUM: '#eab308', 
  LOW: '#22c55e' 
};

export default function RiskDonutChart({ data }) {
  // data: [{ name: 'CRITICAL', value: 3 }, ...]
  if (!data || data.length === 0) return null;
  
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie 
          data={data} 
          cx="50%" 
          cy="50%" 
          innerRadius={55} 
          outerRadius={80}
          paddingAngle={3} 
          dataKey="value" 
          stroke="none"
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] || '#64748b'} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ 
            background: '#0f2044', 
            border: '1px solid rgba(255,255,255,0.1)', 
            borderRadius: 12 
          }}
          itemStyle={{ color: '#cbd5e1' }}
        />
        <Legend
          iconType="circle" 
          iconSize={8}
          formatter={(value) => (
            <span style={{ color: '#94a3b8', fontSize: 11 }}>{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
