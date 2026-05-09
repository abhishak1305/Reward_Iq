import React from 'react';
import { FiSave } from 'react-icons/fi';

const Settings = () => {
  const role = localStorage.getItem('userRole') || 'admin';

  if (role === 'employee') {
    return (
      <div className="dashboard animate-fade-in">
        <div className="dashboard-header">
          <div>
            <h1>My Preferences</h1>
            <p>Customize your personal account settings and notifications.</p>
          </div>
          <button className="btn btn-primary" onClick={() => alert('Preferences saved!')}>
            <FiSave /> Save Preferences
          </button>
        </div>

        <div className="glass-panel" style={{ maxWidth: '600px' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Notification Preferences</h3>
          <form>
            <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input type="checkbox" id="email_notif" defaultChecked />
              <label htmlFor="email_notif" style={{ cursor: 'pointer' }}>Email Notifications for New Rewards</label>
            </div>
            <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input type="checkbox" id="feedback_notif" defaultChecked />
              <label htmlFor="feedback_notif" style={{ cursor: 'pointer' }}>Alert me when I receive Peer Feedback</label>
            </div>
            
            <h3 style={{ marginTop: '2.5rem', marginBottom: '1.5rem' }}>Account Details</h3>
            <div className="form-group">
              <label className="form-label">Preferred Display Name</label>
              <input type="text" className="form-input" defaultValue="Employee User" />
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h1>System Settings</h1>
          <p>Configure organization-wide application preferences.</p>
        </div>
        <button className="btn btn-primary" onClick={() => alert('System Settings saved!')}>
          <FiSave /> Save System Settings
        </button>
      </div>

      <div className="glass-panel" style={{ maxWidth: '600px' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>Global Organization Settings</h3>
        <form>
          <div className="form-group">
            <label className="form-label">Organization Name</label>
            <input type="text" className="form-input" defaultValue="RewardIQ Enterprise" />
          </div>
          <div className="form-group">
            <label className="form-label">Admin Contact Email</label>
            <input type="email" className="form-input" defaultValue="admin@rewardiq.com" />
          </div>
          
          <h3 style={{ marginTop: '2.5rem', marginBottom: '1.5rem' }}>AI Module Configuration</h3>
          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <input type="checkbox" id="ai_sentiment" defaultChecked />
            <label htmlFor="ai_sentiment" style={{ cursor: 'pointer' }}>Enable Automated Sentiment Analysis</label>
          </div>
          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <input type="checkbox" id="ai_fairness" defaultChecked />
            <label htmlFor="ai_fairness" style={{ cursor: 'pointer' }}>Run Weekly Fairness & Bias Detection Reports</label>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings;
