import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { FiTrendingUp, FiUsers, FiAward, FiActivity, FiZap, FiTarget, FiShield, FiMessageSquare } from 'react-icons/fi';
import { apiFetch } from '../lib/api';
import './Dashboard.css';

const StatCard = ({ title, value, change, icon: Icon, color }) => (
  <div className="glass-panel stat-card animate-fade-in">
    <div className="stat-header">
      <div>
        <p className="stat-title">{title}</p>
        <h3 className="stat-value">{value}</h3>
      </div>
      <div className={`stat-icon`} style={{ color, background: `${color}20` }}>
        <Icon />
      </div>
    </div>
    <div className="stat-footer">
      <span className={`stat-change ${change.startsWith('-') ? 'negative' : 'positive'}`}>
        {change}
      </span>
      <span className="stat-period">vs last month</span>
    </div>
  </div>
);

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#8b5cf6', '#ec4899'];

const Dashboard = () => {
  const role = localStorage.getItem('userRole') || 'admin';
  const [overview, setOverview] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [aiInsights, setAiInsights] = useState(null);
  const [fairnessReport, setFairnessReport] = useState(null);
  const [orgSentiment, setOrgSentiment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      // Don't set global loading to true on every poll to avoid flickering
      // but do it on first load.
      if (!overview) setLoading(true);
      
      try {
        if (role === 'admin') {
          // Fetch independently to be resilient
          apiFetch('/analytics/overview').then(setOverview).catch(console.error);
          apiFetch('/analytics/attendance-trend').then(tr => {
            const mappedTrend = tr.map(t => ({ name: t.month, value: t.attendance_rate * 100 }));
            setTrendData(mappedTrend.length > 0 ? mappedTrend : [{name: 'No data', value: 0}]);
          }).catch(console.error);
          apiFetch('/ai/fairness').then(setFairnessReport).catch(console.error);
          apiFetch('/ai/sentiment/org').then(setOrgSentiment).catch(console.error);
        } else {
          const me = await apiFetch('/employees/me');
          setOverview(me);
          apiFetch(`/ai/insights/${me.id}`).then(setAiInsights).catch(console.error);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
    const interval = setInterval(loadData, 30000); // Poll every 30 seconds
    return () => clearInterval(interval);
  }, [role]);

  if (loading) return <div className="dashboard">Loading...</div>;

  if (role === 'employee') {
    return (
      <div className="dashboard">
        <div className="dashboard-header animate-fade-in">
          <div>
            <h1>My Dashboard</h1>
            <p>Welcome back! Here's your personal performance overview.</p>
          </div>
        </div>

        <div className="stats-grid">
          <StatCard title="My Productivity" value={`${overview?.productivity_score || 0}%`} change="+2%" icon={FiTrendingUp} color="#10b981" />
          <StatCard title="My Reward Points" value={overview?.reward_points || 0} change="+150" icon={FiAward} color="#f59e0b" />
          <StatCard title="Overall Mood" value={aiInsights?.sentiment_label || 'Neutral'} change="Stable" icon={FiActivity} color="#6366f1" />
        </div>

        <div className="dashboard-content" style={{ marginTop: '2rem' }}>
          <div className="glass-panel animate-fade-in" style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#6366f1' }}><FiZap /></div>
              <h3>AI Performance Insights</h3>
            </div>
            <div className="ai-insight-content">
              <p style={{ fontSize: '1.1rem', color: '#e2e8f0', lineHeight: '1.6' }}>
                {aiInsights?.insight_text || "Analyzing your data to provide personalized recommendations..."}
              </p>
              {aiInsights?.suggested_action && (
                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
                  <strong style={{ color: '#10b981', display: 'block', marginBottom: '0.25rem' }}>Next Action Item:</strong>
                  <span style={{ color: '#cbd5e1' }}>{aiInsights.suggested_action}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header animate-fade-in">
        <div>
          <h1>Dashboard Overview</h1>
          <p>Welcome back! Here's what's happening with your team today.</p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard title="Total Employees" value={overview?.total_employees || 0} change="+12%" icon={FiUsers} color="#6366f1" />
        <StatCard title="Avg Productivity" value={`${overview?.avg_productivity_score || 0}%`} change="+5%" icon={FiTrendingUp} color="#10b981" />
        <StatCard title="Rewards Given" value={overview?.total_rewards_given || 0} change="+24" icon={FiAward} color="#f59e0b" />
        <StatCard title="Feedback Count" value={overview?.total_feedback_entries || 0} change="+8" icon={FiMessageSquare} color="#10b981" />
        <StatCard title="Org Sentiment" value={orgSentiment?.label || 'Neutral'} change="Positive" icon={FiActivity} color="#f43f5e" />
      </div>

      <div className="dashboard-content grid-2">
        {/* Attendance Chart */}
        <div className="glass-panel animate-fade-in">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <FiTarget color="#6366f1" />
            <h3>Attendance Trends</h3>
          </div>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="value" stroke="#6366f1" fillOpacity={1} fill="url(#colorVal)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fairness Analysis */}
        <div className="glass-panel animate-fade-in">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <FiShield color="#10b981" />
            <h3>Fairness Audit</h3>
          </div>
          <div style={{ height: '300px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="fairness-score" style={{ textAlign: 'center', padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px' }}>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase' }}>Equity Score</span>
              <h2 style={{ fontSize: '2.5rem', color: '#10b981', margin: '0.25rem 0' }}>
                {( (fairnessReport?.overall_fairness_score || 0) * 100).toFixed(0)}%
              </h2>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                {fairnessReport?.recommendations?.[0] || "Audit complete."}
              </p>
            </div>
            
            <div style={{ flex: 1, overflow: 'auto' }}>
              <h4 style={{ marginBottom: '0.75rem', fontSize: '0.9rem', color: '#94a3b8' }}>Risk Factors</h4>
              {fairnessReport?.bias_flags?.length > 0 ? (
                fairnessReport.bias_flags.map((flag, i) => (
                  <div key={i} style={{ padding: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '0.85rem', color: '#f43f5e' }}>
                    {flag}
                  </div>
                ))
              ) : (
                <p style={{ color: '#94a3b8', fontSize: '0.9rem', textAlign: 'center', marginTop: '1rem' }}>No disparities detected.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
