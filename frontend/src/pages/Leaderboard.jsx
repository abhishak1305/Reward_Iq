import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiTrendingUp } from 'react-icons/fi';
import { apiFetch } from '../lib/api';

const Leaderboard = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch('/employees/ranking?limit=10')
      .then(data => setUsers(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="dashboard">Loading...</div>;

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h1>Leaderboard</h1>
          <p>See how you stack up against your peers this month.</p>
        </div>
      </div>

      <div className="glass-panel" style={{ maxWidth: '800px' }}>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <th style={{ padding: '1rem', color: '#94a3b8', width: '80px' }}>Rank</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Employee</th>
              <th style={{ padding: '1rem', color: '#94a3b8', textAlign: 'right' }}>Points</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.rank} style={{ 
                borderBottom: '1px solid rgba(255,255,255,0.05)',
              }}>
                <td style={{ padding: '1rem', fontWeight: 'bold', fontSize: '1.2rem', color: user.rank <= 3 ? '#f59e0b' : '#e2e8f0' }}>
                  #{user.rank}
                </td>
                <td style={{ padding: '1rem' }}>
                  <div 
                    onClick={() => navigate(`/employees/${user.employee_id}`)}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
                    className="hover-bright"
                  >
                    <div className="avatar small" style={{ background: user.rank <= 3 ? 'var(--primary)' : '#475569' }}>
                      {user.full_name.charAt(0)}
                    </div>
                    <span style={{ fontWeight: '500' }}>
                      {user.full_name}
                    </span>
                  </div>
                </td>
                <td style={{ padding: '1rem', textAlign: 'right' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <span style={{ fontWeight: '600', color: '#10b981' }}>{user.reward_points} pts</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Leaderboard;
