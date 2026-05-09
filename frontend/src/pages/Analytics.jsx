import { useState, useEffect } from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { FiPieChart, FiBarChart2, FiTarget, FiShield } from 'react-icons/fi';
import { apiFetch } from '../lib/api';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#8b5cf6', '#ec4899', '#06b6d4'];

const Analytics = () => {
  const role = localStorage.getItem('userRole') || 'admin';
  const [deptData, setDeptData] = useState([]);
  const [rewardDist, setRewardDist] = useState([]);
  const [fairness, setFairness] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (role === 'admin') {
      const loadData = async () => {
        try {
          const [d, r, f] = await Promise.all([
            apiFetch('/analytics/department-performance'),
            apiFetch('/analytics/reward-distribution'),
            apiFetch('/ai/fairness')
          ]);
          setDeptData(d);
          setRewardDist(r);
          setFairness(f);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      loadData();
    } else {
      setLoading(false);
    }
  }, [role]);

  if (loading) return <div className="dashboard">Loading Analytics...</div>;

  if (role === 'employee') {
    return (
      <div className="dashboard animate-fade-in">
        <div className="glass-panel" style={{ textAlign: 'center', padding: '4rem' }}>
          <h2>Access Denied</h2>
          <p>You do not have permission to view organizational analytics.</p>
        </div>
      </div>
    );
  }

  // Map data for Radar Chart
  const radarData = deptData.map(d => ({
    subject: d.department,
    productivity: d.avg_productivity,
    rewards: (d.avg_reward_points / 20), // Normalize for radar
    fullMark: 100,
  }));

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h1>Organizational Analytics</h1>
          <p>Data-driven insights into team performance and reward equity.</p>
        </div>
      </div>

      <div className="grid-2">
        {/* Department Comparison Radar */}
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <FiTarget color="#6366f1" />
            <h3>Department Performance vs. Rewards</h3>
          </div>
          <div style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name="Productivity %" dataKey="productivity" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
                <Radar name="Rewards (Scaled)" dataKey="rewards" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                <Tooltip 
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Reward Distribution Pie */}
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <FiPieChart color="#f59e0b" />
            <h3>Reward Distribution by Type</h3>
          </div>
          <div style={{ height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={rewardDist}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="type"
                  label={({name, percent}) => `${name.replace('_', ' ')} ${(percent * 100).toFixed(0)}%`}
                >
                  {rewardDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="dashboard-content" style={{ gridTemplateColumns: '1fr', marginTop: '1.5rem' }}>
        {/* Fairness Audit Bar Chart */}
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <FiShield color="#10b981" />
            <h3>Reward Equity Audit (Points per Productivity Unit)</h3>
          </div>
          <div style={{ height: '350px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="department" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Bar dataKey="avg_reward_points" name="Avg Reward Points" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
             <p style={{ margin: 0, color: '#e2e8f0' }}>
               <strong>AI Conclusion:</strong> {fairness?.recommendations?.[0] || "Analyzing reward parity across the organization..."}
             </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
