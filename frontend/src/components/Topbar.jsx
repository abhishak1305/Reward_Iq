import React, { useState } from 'react';
import { FiBell, FiSearch, FiUser, FiMenu } from 'react-icons/fi';
import Modal from './Modal';
import { apiFetch } from '../lib/api';
import { useLayout } from '../context/LayoutContext';
import './Topbar.css';

const Topbar = () => {
  const { toggleMobileMenu } = useLayout();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchResultOpen, setIsSearchResultOpen] = useState(false);
  const [searchResult, setSearchResult] = useState(null);
  
  const [notifications, setNotifications] = useState([]);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const role = localStorage.getItem('userRole') || 'admin';
  const name = localStorage.getItem('userName') || 'Admin User';
  const displayRole = role === 'admin' ? 'HR Director' : 'Software Engineer';

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery) return;
    
    try {
      const employees = await apiFetch('/employees');
      const result = employees.find(emp => emp.full_name.toLowerCase().includes(searchQuery.toLowerCase()));
      
      setSearchResult(result || null);
      setIsSearchResultOpen(true);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchNotifications = async () => {
    try {
      const data = await apiFetch('/notifications');
      setNotifications(data);
      setUnreadCount(data.filter(n => !n.is_read).length);
    } catch (e) {
      console.error(e);
    }
  };

  // Poll notifications on mount
  React.useEffect(() => {
    fetchNotifications();
  }, []);

  const handleOpenNotif = () => {
    fetchNotifications();
    setIsNotifOpen(true);
  };

  const handleMarkAllRead = async () => {
    try {
      await apiFetch('/notifications/read-all', { method: 'PATCH' });
      await fetchNotifications();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="topbar">
      <button className="hamburger" onClick={toggleMobileMenu}>
        <FiMenu />
      </button>
      {role === 'admin' ? (
        <form className="search-bar" onSubmit={handleSearch}>
          <FiSearch className="search-icon" />
          <input 
            type="text" 
            placeholder="Search employees..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      ) : (
        <div className="search-bar"></div>
      )}
      
      <div className="topbar-actions">
        <button className="icon-btn" onClick={handleOpenNotif}>
          <FiBell />
          {unreadCount > 0 && <span className="notification-dot"></span>}
        </button>
        <div className="user-profile">
          <div className="avatar">
            <FiUser />
          </div>
          <div className="user-info">
            <span className="user-name">{name}</span>
            <span className="user-role">{displayRole}</span>
          </div>
        </div>
      </div>
      <Modal isOpen={isSearchResultOpen} onClose={() => setIsSearchResultOpen(false)} title="Search Result">
        {searchResult ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="avatar" style={{ width: '60px', height: '60px', fontSize: '1.5rem' }}>
                {searchResult.full_name.charAt(0)}
              </div>
              <div>
                <h3 style={{ margin: 0 }}>{searchResult.full_name}</h3>
                <p style={{ margin: 0, color: '#94a3b8' }}>{searchResult.position} • {searchResult.department}</p>
              </div>
            </div>
            
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.5rem', color: '#e2e8f0' }}>Performance Evaluation Path</h4>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#94a3b8' }}>Productivity Score:</span>
                <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>{searchResult.productivity_score}%</span>
              </div>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#f43f5e' }}>
            <p>No employee found matching "{searchQuery}"</p>
          </div>
        )}
      </Modal>

      <Modal isOpen={isNotifOpen} onClose={() => setIsNotifOpen(false)} title="Notifications">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <span>You have {unreadCount} unread messages</span>
          {unreadCount > 0 && (
            <button className="btn" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }} onClick={handleMarkAllRead}>
              Mark All Read
            </button>
          )}
        </div>
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {notifications.length === 0 ? (
            <p style={{ color: '#94a3b8', textAlign: 'center' }}>No notifications.</p>
          ) : (
            notifications.map(n => (
              <div key={n.id} style={{ 
                padding: '1rem', 
                background: n.is_read ? 'rgba(255,255,255,0.02)' : 'rgba(99, 102, 241, 0.1)', 
                marginBottom: '0.5rem', 
                borderRadius: '8px',
                borderLeft: n.is_read ? 'none' : '3px solid #6366f1'
              }}>
                <h4 style={{ margin: '0 0 0.5rem 0' }}>{n.title}</h4>
                <p style={{ margin: 0, fontSize: '0.9rem', color: '#cbd5e1' }}>{n.message}</p>
                <small style={{ color: '#94a3b8', display: 'block', marginTop: '0.5rem' }}>
                  {new Date(n.created_at).toLocaleString()}
                </small>
              </div>
            ))
          )}
        </div>
      </Modal>
    </div>
  );
};

export default Topbar;
