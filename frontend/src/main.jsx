import React from 'react';
import {createRoot} from 'react-dom/client';
import DinerApp from './apps/DinerApp.jsx';
import KitchenApp from './apps/KitchenApp.jsx';
import WaiterApp from './apps/WaiterApp.jsx';
import DashboardApp from './apps/DashboardApp.jsx';
const apps={diner:DinerApp,kitchen:KitchenApp,waiter:WaiterApp,dashboard:DashboardApp};
document.querySelectorAll('[data-react-app]').forEach(node=>{const Component=apps[node.dataset.reactApp];if(Component)createRoot(node).render(<Component config={node.dataset}/>);});
