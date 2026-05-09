import { NavLink, useNavigate } from 'react-router-dom';
import { FiHome, FiUsers, FiAward, FiMessageSquare, FiPieChart, FiSettings, FiLogOut, FiBarChart2 } from 'react-icons/fi';
import { useLayout } from '../context/LayoutContext';
import './Sidebar.css';

const Sidebar = () => {
  const navigate = useNavigate();
  const { isMobileMenuOpen, closeMobileMenu } = useLayout();
  const role = localStorage.getItem('userRole') || 'admin';

  const handleLogout = () => {
    localStorage.clear();
    closeMobileMenu();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: FiHome, label: 'Dashboard' },
    { path: '/employees', icon: FiUsers, label: 'Employees' },
    { path: '/rewards', icon: FiAward, label: 'Rewards' },
    { path: '/feedback', icon: FiMessageSquare, label: 'Feedback' },
    { path: '/analytics', icon: FiPieChart, label: 'Analytics' },
    { path: '/leaderboard', icon: FiBarChart2, label: 'Leaderboard' },
    { path: '/settings', icon: FiSettings, label: 'Settings' },
  ];

  return (
    <>
      <div className={`sidebar-overlay ${isMobileMenuOpen ? 'active' : ''}`} onClick={closeMobileMenu}></div>
      <aside className={`sidebar ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-icon">IQ</div>
          <span className="brand-name">RewardIQ</span>
        </div>
        
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink 
              key={item.path} 
              to={item.path} 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-link logout-btn" onClick={handleLogout}>
            <FiLogOut className="nav-icon" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
