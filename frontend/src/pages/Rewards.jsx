import { useState, useEffect } from 'react';
import { FiAward } from 'react-icons/fi';
import { apiFetch } from '../lib/api';
import { useToast } from '../context/ToastContext';

const Rewards = () => {
  const { addToast } = useToast();
  const role = localStorage.getItem('userRole') || 'admin';
  const [rewardsList, setRewardsList] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Form State
  const [newReward, setNewReward] = useState({
    employee_id: '',
    reward_type: 'bonus',
    title: '',
    description: '',
    points: 0
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      if (role === 'employee') {
        const me = await apiFetch('/employees/me');
        const data = await apiFetch(`/rewards/employee/${me.id}`);
        setRewardsList(data);
      } else {
        const [allRewards, allEmployees] = await Promise.all([
          apiFetch('/rewards'),
          apiFetch('/employees')
        ]);
        setRewardsList(allRewards);
        setEmployees(allEmployees);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [role]);

  const handleGiveReward = async (e) => {
    e.preventDefault();
    if (!newReward.employee_id) return alert('Please select an employee');
    setIsSubmitting(true);
    try {
      await apiFetch('/rewards', {
        method: 'POST',
        body: JSON.stringify({
          ...newReward,
          employee_id: parseInt(newReward.employee_id),
          points: parseInt(newReward.points)
        })
      });
      setNewReward({ employee_id: '', reward_type: 'bonus', title: '', description: '', points: 0 });
      fetchData();
      addToast('Recognition Awarded', 'Employee has been notified and points added.', 'success');
    } catch (err) {
      addToast('Error', err.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="skeleton" style={{ width: '300px', height: '40px' }}></div>
      </div>
      <div className="grid-2">
        <div className="skeleton" style={{ height: '500px' }}></div>
        <div className="skeleton" style={{ height: '500px' }}></div>
      </div>
    </div>
  );

  if (role === 'employee') {
    return (
      <div className="dashboard animate-fade-in">
        <div className="dashboard-header">
          <div>
            <h1>My Rewards</h1>
            <p>View your earned rewards and recognition.</p>
          </div>
        </div>

        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem' }}>My Recent Rewards</h3>
          <ul className="performer-list">
            {rewardsList.map((item) => (
              <li key={item.id} className="performer-item">
                <div className="performer-info">
                  <div className="avatar small" style={{ background: 'var(--accent)' }}>
                    <FiAward />
                  </div>
                  <div>
                    <h4>{item.title}</h4>
                    <p>{item.description} • <span style={{ color: '#94a3b8' }}>{new Date(item.awarded_at).toLocaleDateString()}</span></p>
                  </div>
                </div>
                <div className="performer-score">
                  <span className="badge badge-warning">+{item.points} pts</span>
                </div>
              </li>
            ))}
            {rewardsList.length === 0 && <p style={{ color: '#94a3b8' }}>No rewards found.</p>}
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h1>Rewards Management</h1>
          <p>Recognize top performance and award achievement points.</p>
        </div>
      </div>

      <div className="dashboard-content grid-2">
        {/* Give Reward Form */}
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem' }}>Award New Recognition</h3>
          <form onSubmit={handleGiveReward}>
            <div className="form-group">
              <label className="form-label">Recipient</label>
              <select 
                className="form-input"
                value={newReward.employee_id}
                onChange={(e) => setNewReward({...newReward, employee_id: e.target.value})}
                required
              >
                <option value="">Select an employee...</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>{emp.full_name} ({emp.department})</option>
                ))}
              </select>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Reward Type</label>
                <select 
                  className="form-input"
                  value={newReward.reward_type}
                  onChange={(e) => setNewReward({...newReward, reward_type: e.target.value})}
                >
                  <option value="bonus">Performance Bonus</option>
                  <option value="badge">Skill Badge</option>
                  <option value="certificate">Milestone Certificate</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Points</label>
                <input 
                  type="number" 
                  className="form-input"
                  value={newReward.points}
                  onChange={(e) => setNewReward({...newReward, points: e.target.value})}
                  min="0"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Title</label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. Employee of the Month"
                value={newReward.title}
                onChange={(e) => setNewReward({...newReward, title: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Reason / Description</label>
              <textarea 
                className="form-input" 
                style={{ minHeight: '100px' }}
                placeholder="Describe why this reward is being given..."
                value={newReward.description}
                onChange={(e) => setNewReward({...newReward, description: e.target.value})}
                required
              ></textarea>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={isSubmitting}>
              {isSubmitting ? 'Processing...' : 'Assign Reward'}
            </button>
          </form>
        </div>

        {/* Global History */}
        <div className="glass-panel">
          <h3 style={{ marginBottom: '1.5rem' }}>Global Reward History</h3>
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <ul className="performer-list">
              {rewardsList.map((item) => {
                const emp = employees.find(e => e.id === item.employee_id);
                return (
                  <li key={item.id} className="performer-item" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '1rem' }}>
                    <div className="performer-info">
                      <div className="avatar small" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}>
                        <FiAward />
                      </div>
                      <div>
                        <h4 style={{ margin: 0 }}>{item.title}</h4>
                        <p style={{ margin: '0.25rem 0', fontSize: '0.9rem', color: '#94a3b8' }}>
                          To: <span style={{ color: '#e2e8f0' }}>{emp?.full_name || 'Employee'}</span>
                        </p>
                        <p style={{ margin: 0, fontSize: '0.85rem' }}>{item.description}</p>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="badge badge-warning" style={{ marginBottom: '0.5rem' }}>+{item.points} pts</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{new Date(item.awarded_at).toLocaleDateString()}</div>
                    </div>
                  </li>
                );
              })}
              {rewardsList.length === 0 && <p style={{ color: '#94a3b8', textAlign: 'center' }}>No rewards history found.</p>}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Rewards;
