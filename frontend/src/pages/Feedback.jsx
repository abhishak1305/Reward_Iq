import { useState, useEffect } from 'react';
import { FiUser, FiMessageSquare, FiSend, FiPlus } from 'react-icons/fi';
import { apiFetch } from '../lib/api';
import Modal from '../components/Modal';

const Feedback = () => {
  const role = localStorage.getItem('userRole') || 'admin';
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [employees, setEmployees] = useState([]);
  
  // Form State
  const [targetEmployeeId, setTargetEmployeeId] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('performance');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
    // Fetch employee list for the dropdown
    apiFetch('/employees')
      .then(data => setEmployees(data))
      .catch(console.error);
  }, [role]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (role === 'admin') {
        // Admins see everything (simplified: fetching first employee's for now as in original)
        const emps = await apiFetch('/employees');
        if (emps.length > 0) {
          const data = await apiFetch(`/feedback/employee/${emps[0].id}`);
          setFeedbackList(data);
        }
      } else {
        // Employees see feedback GIVEN TO THEM
        const me = await apiFetch('/employees/me');
        const data = await apiFetch(`/feedback/employee/${me.id}`);
        setFeedbackList(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!targetEmployeeId || !content) return;

    setIsSubmitting(true);
    try {
      await apiFetch('/feedback', {
        method: 'POST',
        body: JSON.stringify({
          employee_id: parseInt(targetEmployeeId),
          content,
          category
        })
      });
      setIsModalOpen(false);
      setContent('');
      setTargetEmployeeId('');
      // Refresh list if the feedback was for 'me' (for employees) or just refresh general list
      fetchData();
    } catch (err) {
      alert(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <div className="dashboard">Loading...</div>;

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h1>360-Degree Feedback</h1>
          <p>{role === 'admin' ? 'Monitor organizational performance and peer insights.' : 'View your peer recognition and insights.'}</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <FiPlus /> Give Feedback
        </button>
      </div>

      <div className="glass-panel" style={{ overflowX: 'auto' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>{role === 'admin' ? 'Recent Peer Feedback' : 'Feedback Received'}</h3>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Recipient</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Sentiment</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Comment</th>
              <th style={{ padding: '1rem', color: '#94a3b8' }}>Date</th>
            </tr>
          </thead>
          <tbody>
            {feedbackList.map((item) => (
              <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '1rem', whiteSpace: 'nowrap' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <FiUser color="#6366f1" /> {employees.find(e => e.id === item.employee_id)?.full_name || `Emp #${item.employee_id}`}
                  </div>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span className={`badge ${item.sentiment_label === 'positive' ? 'badge-success' : 'badge-primary'}`}>
                    {item.sentiment_label || 'neutral'}
                  </span>
                </td>
                <td style={{ padding: '1rem', color: '#cbd5e1', maxWidth: '400px' }}>
                  "{item.content}"
                </td>
                <td style={{ padding: '1rem', color: '#94a3b8', whiteSpace: 'nowrap' }}>{new Date(item.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {feedbackList.length === 0 && (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
            <FiMessageSquare size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <p>No feedback found yet.</p>
          </div>
        )}
      </div>

      {/* Give Feedback Modal */}
      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        title="Submit Peer Feedback"
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Recipient</label>
            <select 
              className="form-input"
              value={targetEmployeeId}
              onChange={(e) => setTargetEmployeeId(e.target.value)}
              required
            >
              <option value="">Choose an employee...</option>
              {employees.map(emp => (
                <option key={emp.id} value={emp.id}>{emp.full_name} ({emp.department})</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Category</label>
            <select 
              className="form-input"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="performance">Performance</option>
              <option value="teamwork">Teamwork</option>
              <option value="attendance">Attendance</option>
              <option value="general">General</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Your Feedback</label>
            <textarea 
              className="form-input"
              style={{ minHeight: '120px', resize: 'vertical' }}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What would you like to say? Be constructive and professional..."
              required
            ></textarea>
            <p style={{ fontSize: '0.8rem', marginTop: '0.5rem', color: '#94a3b8' }}>
              Your feedback will be automatically analyzed for sentiment and shared with HR.
            </p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
            <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : <><FiSend /> Submit Feedback</>}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Feedback;
