import { Outlet } from 'react-router-dom';
import Topbar from './Topbar';
import '../../styles/layout.css';

export default function AppLayout() {
  return (
    <div className="app-layout-horizontal">
      <Topbar />
      <main className="main-content-horizontal">
        <Outlet />
      </main>
    </div>
  );
}
