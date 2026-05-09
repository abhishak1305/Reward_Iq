import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiAward, FiTrendingUp, FiMessageSquare, FiCalendar, FiBriefcase, FiZap, FiCheckCircle } from 'react-icons/fi';
import { apiFetch } from '../lib/api';
import './Dashboard.css';

const EmployeeProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [feedback, setFeedback] = useState([]);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      setLoading(true);
      try {
        // Load basic info first
        const emp = await apiFetch(`/employees/${id}`);
        setEmployee(emp);
        
        // Then try to load secondary data (don't crash if these fail)
        try {
          const [fb, insights] = await Promise.all([
            apiFetch(`/feedback?employee_id=${id}`),
            apiFetch(`/ai/insights/${id}`)
          ]);
          setFeedback(fb || []);
          setAiInsights(insights);
        } catch (e) {
          console.warn("Secondary data load failed:", e);
        }
      } catch (err) {
        console.error("Profile load failed:", err);
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [id]);

  if (loading) return <div className="dashboard">Loading Profile...</div>;
  if (!employee) return <div className="dashboard">Employee not found.</div>;

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <button onClick={() => navigate(-1)} className="btn btn-outline" style={{ padding: '0.5rem 1rem' }}>
          <FiArrowLeft /> Back
        </button>
      </div>

      <div className="dashboard-content" style={{ gridTemplateColumns: '1fr 2fr' }}>
        {/* Sidebar: Basic Info */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div className="avatar" style={{ width: '120px', height: '120px', margin: '0 auto 1.5rem', fontSize: '3rem' }}>
              {employee.full_name.charAt(0)}
            </div>
            <h2 style={{ margin: 0 }}>{employee.full_name}</h2>
            <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>{employee.position}</p>
          </div>

          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: '#cbd5e1' }}>
              <FiBriefcase color="#6366f1" /> <span>{employee.department}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: '#cbd5e1' }}>
              <FiCalendar color="#6366f1" /> <span>Hired {new Date(employee.hire_date).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="stats-list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="stat-card" style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.1)' }}>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Productivity</span>
              <h3 style={{ margin: 0, color: '#10b981' }}>{employee.productivity_score}%</h3>
            </div>
            <div className="stat-card" style={{ padding: '1rem', background: 'rgba(245, 158, 11, 0.1)' }}>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Reward Points</span>
              <h3 style={{ margin: 0, color: '#f59e0b' }}>{employee.reward_points} pts</h3>
            </div>
          </div>
        </div>

        {/* Main Content: AI Insights & Feedback */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* AI Section */}
          <div className="glass-panel" style={{ border: '1px solid rgba(99, 102, 241, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#6366f1' }}><FiZap /></div>
              <h3>AI Performance Summary</h3>
            </div>
            <p style={{ fontSize: '1.1rem', color: '#e2e8f0', lineHeight: '1.6', marginBottom: '1.5rem' }}>
              {aiInsights?.summary || "No insights available yet."}
            </p>
            
            <div className="grid-2">
              <div>
                <h4 style={{ marginBottom: '1rem', color: '#10b981' }}>Strengths</h4>
                {aiInsights?.strengths.map((s, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#cbd5e1' }}>
                    <FiCheckCircle color="#10b981" /> <span>{s}</span>
                  </div>
                ))}
              </div>
              <div>
                <h4 style={{ marginBottom: '1rem', color: '#f43f5e' }}>Areas for Growth</h4>
                {aiInsights?.areas_for_improvement.map((a, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#cbd5e1' }}>
                    <span style={{ color: '#f43f5e' }}>•</span> <span>{a}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Feedback Section */}
          <div className="glass-panel">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}><FiMessageSquare /></div>
              <h3>Recent Feedback</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {feedback.length === 0 ? (
                <p style={{ color: '#94a3b8', textAlign: 'center', padding: '2rem' }}>No feedback entries yet.</p>
              ) : (
                feedback.map((fb) => (
                  <div key={fb.id} style={{ 
                    padding: '1.25rem', 
                    background: 'rgba(255,255,255,0.03)', 
                    borderRadius: '12px',
                    borderLeft: `4px solid ${fb.sentiment_label === 'positive' ? '#10b981' : fb.sentiment_label === 'negative' ? '#f43f5e' : '#94a3b8'}`
                  }}>
                    <p style={{ margin: 0, lineHeight: '1.5', color: '#e2e8f0' }}>"{fb.content}"</p>
                    <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className={`badge badge-${fb.sentiment_label === 'positive' ? 'success' : fb.sentiment_label === 'negative' ? 'danger' : 'warning'}`}>
                        {fb.sentiment_label.toUpperCase()}
                      </span>
                      <small style={{ color: '#94a3b8' }}>{new Date(fb.created_at).toLocaleDateString()}</small>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeProfile;
