import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Home from './pages/Home';

function App() {
	const { isAuthenticated } = useAuth();

	return (
		<div className="app">
			<Router>
				<Routes>
					<Route path="/" element={isAuthenticated ? (<Navigate to="/home" />) : (<Login />)} />
					<Route path="/home" element={isAuthenticated ? (<Home />) : (<Navigate to="/" />)} />
				</Routes>
			</Router>
		</div>
	);
};

export default App;
