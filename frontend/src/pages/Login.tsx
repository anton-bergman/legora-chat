import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");

  const handleLogin = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate("/home");
    } catch (error) {
      console.error("Login failed", error);
      setError("Login failed. Please check your username and password.");
    }
  };

  return (
    <div className="flex flex-col items-center">
      <h1 className="font-bold mb-10">Legora Chat</h1>
      <div className="flex flex-col gap-4 w-100 border border-white rounded-md p-4">
        <h1 className="font-semibold mb-4">Login</h1>
        {error && <div className="error-message text-red-500">{error}</div>}
        <form>
          <div className="flex flex-col gap-1">
            <label>Username</label>
            <input
              className="border border-white rounded p-1"
              type="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label>Password</label>
            <input
              className="border border-white rounded p-1"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
          </div>
          <button className="mt-4" type="submit" onClick={handleLogin}>
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
