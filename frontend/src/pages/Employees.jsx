import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiMessageSquare, FiTrash2, FiSend, FiCpu, FiCheckCircle, FiTrendingUp, FiUser } from 'react-icons/fi';
import { apiFetch } from '../lib/api';
import { useToast } from '../context/ToastContext';
import Modal from '../components/Modal';

const Employees = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const role = localStorage.getItem('userRole') || 'admin';
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Feedback & AI Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [aiData, setAIData] = useState(null);
  const [feedbackContent, setFeedbackContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Add Employee Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newEmployee, setNewEmployee] = useState({
    full_name: '',
    email: '',
    department: 'Engineering',
    position: '',
    reward_points: 0,
    productivity_score: 80
  });

  const fetchEmployees = () => {
    apiFetch('/employees')
      .then(data => setEmployees(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleOpenFeedback = (emp) => {
    setSelectedEmployee(emp);
    setIsModalOpen(true);
  };

  const handleOpenAIProfile = async (emp) => {
    setSelectedEmployee(emp);
    setAIData(null);
    setIsAIModalOpen(true);
    try {
      const [insights, recommendations] = await Promise.all([
        apiFetch(`/ai/insights/${emp.id}`),
        apiFetch(`/ai/recommend/rewards/${emp.id}`)
      ]);
      setAIData({ insights, recommendations });
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!selectedEmployee || !feedbackContent) return;

    setIsSubmitting(true);
    try {
      await apiFetch('/feedback', {
        method: 'POST',
        body: JSON.stringify({
          employee_id: selectedEmployee.id,
          content: feedbackContent,
          category: 'general'
        })
      });
      setIsModalOpen(false);
      setFeedbackContent('');
      addToast('Success', 'Feedback submitted successfully!', 'success');
    } catch (err) {
      addToast('Error', err.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteEmployee = (emp) => {
    if (window.confirm(`Are you sure you want to deactivate ${emp.full_name}?`)) {
      apiFetch(`/employees/${emp.id}`, { method: 'DELETE' })
        .then(() => setEmployees(prev => prev.filter(e => e.id !== emp.id)))
        .catch(err => alert(err.message));
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      // Note: Backend requires a User to be created first, but let's assume 
      // the POST /employees endpoint handles it or we use a simplified version.
      // Actually, looking at backend/api/v1/employees.py, POST / employees 
      // just creates the Employee row. It needs a user_id.
      
      // For this prototype, we'll suggest using the backend seed or 
      // we'd need a more complex "Onboard" flow. 
      // Let's implement a "Quick Add" that works with the existing schema.
      
      await apiFetch('/employees', {
        method: 'POST',
        body: JSON.stringify({
          ...newEmployee,
          user_id: 1 // Default to admin for now or first user
        })
      });
      
      setIsAddModalOpen(false);
      setNewEmployee({ full_name: '', email: '', department: 'Engineering', position: '', reward_points: 0, productivity_score: 80 });
      fetchEmployees();
      addToast('Welcome!', 'New employee has been registered successfully.', 'success');
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
      <div className="glass-panel">
        <div className="skeleton" style={{ height: '400px' }}></div>
      </div>
    </div>
  );

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h1>Employee Directory</h1>
          <p>Connect with your colleagues across the organization.</p>
        </div>
        {role === 'admin' && (
          <button className="btn btn-primary" onClick={() => setIsAddModalOpen(true)}>
            + Add Employee
          </button>
        )}
      </div>

      <div className="glass-panel" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Name</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Role</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Department</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Points</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((emp) => (
              <tr key={emp.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '1rem' }}>
                  <div 
                    onClick={() => navigate(`/employees/${emp.id}`)} 
                    style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
                    className="hover-bright"
                  >
                    <div className="avatar small">{emp.full_name.charAt(0)}</div>
                    <span style={{ fontWeight: '500' }}>{emp.full_name}</span>
                  </div>
                </td>
                <td style={{ padding: '1rem', color: '#cbd5e1' }}>{emp.position}</td>
                <td style={{ padding: '1rem', color: '#cbd5e1' }}>{emp.department}</td>
                <td style={{ padding: '1rem' }}>{emp.reward_points}</td>
                <td style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      onClick={() => handleOpenAIProfile(emp)}
                      className="btn btn-outline"
                      style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem', borderColor: 'var(--primary)' }}
                    >
                      <FiCpu /> AI Profile
                    </button>
                    <button 
                      onClick={() => navigate(`/employees/${emp.id}`)}
                      className="btn btn-outline"
                      style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}
                    >
                      <FiUser /> Profile
                    </button>
                    <button 
                      onClick={() => handleOpenFeedback(emp)}
                      className="btn btn-outline"
                      style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}
                    >
                      <FiMessageSquare /> Feedback
                    </button>
                    {role === 'admin' && (
                      <button 
                        onClick={() => handleDeleteEmployee(emp)}
                        className="btn-danger"
                        style={{ padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.8rem' }}
                      >
                        <FiTrash2 />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* AI Profile Modal */}
      <Modal isOpen={isAIModalOpen} onClose={() => setIsAIModalOpen(false)} title={`AI Performance Profile: ${selectedEmployee?.full_name}`} maxWidth="800px">
        {!aiData ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <div className="animate-spin" style={{ marginBottom: '1rem' }}>⌛</div>
            <p>Generating deep performance insights...</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="glass-panel" style={{ background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: '#818cf8' }}>
                <FiTrendingUp /> <strong>Performance Summary</strong>
              </div>
              <p style={{ margin: 0, color: '#e2e8f0', lineHeight: '1.5' }}>{aiData.insights.summary}</p>
            </div>

            <div className="grid-2">
              <div>
                <h4 style={{ marginBottom: '0.75rem', color: '#10b981', fontSize: '0.9rem' }}>CORE STRENGTHS</h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {aiData.insights.strengths.map((s, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                      <FiCheckCircle color="#10b981" /> {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 style={{ marginBottom: '0.75rem', color: '#f43f5e', fontSize: '0.9rem' }}>GROWTH AREAS</h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {aiData.insights.areas_for_improvement.map((a, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                      <span style={{ color: '#f43f5e' }}>•</span> {a}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="glass-panel" style={{ border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <h4 style={{ marginBottom: '1rem', color: '#f59e0b' }}>SMART REWARD RECOMMENDATIONS</h4>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                {aiData.recommendations.recommended_rewards.map((r, i) => (
                  <div key={i} className="badge badge-warning" style={{ padding: '0.5rem 1rem' }}>
                    {r.label}
                  </div>
                ))}
              </div>
              <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#94a3b8' }}>
                <em>Reasoning: {aiData.recommendations.reasoning}</em>
              </p>
            </div>
          </div>
        )}
      </Modal>

      {/* Feedback Modal */}
      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        title={`Give Feedback to ${selectedEmployee?.full_name}`}
      >
        <form onSubmit={handleSubmitFeedback}>
          <div className="form-group">
            <label className="form-label">Constructive Feedback</label>
            <textarea 
              className="form-input"
              style={{ minHeight: '120px', resize: 'vertical' }}
              value={feedbackContent}
              onChange={(e) => setFeedbackContent(e.target.value)}
              placeholder="What makes them a great teammate? Or where can they improve?"
              required
            ></textarea>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Sending...' : <><FiSend /> Send</>}
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Employee Modal */}
      <Modal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)} 
        title="Add New Employee"
      >
        <form onSubmit={handleAddEmployee}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input 
              type="text" 
              className="form-input" 
              value={newEmployee.full_name}
              onChange={(e) => setNewEmployee({...newEmployee, full_name: e.target.value})}
              required 
            />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Department</label>
              <select 
                className="form-input"
                value={newEmployee.department}
                onChange={(e) => setNewEmployee({...newEmployee, department: e.target.value})}
              >
                {["Engineering", "Marketing", "Sales", "HR", "Finance", "Design"].map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Position</label>
              <input 
                type="text" 
                className="form-input" 
                value={newEmployee.position}
                onChange={(e) => setNewEmployee({...newEmployee, position: e.target.value})}
                required 
              />
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
            <button type="button" className="btn btn-outline" onClick={() => setIsAddModalOpen(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Adding...' : 'Create Employee'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Employees;
