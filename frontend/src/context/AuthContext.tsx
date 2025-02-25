import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { io, Socket } from "socket.io-client";

interface AuthContextType {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  user: string | null;
  token: string | null;
  socket: Socket | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    if (token) {
      const newSocket = io("http://127.0.0.1:5000", {
        query: { token: token },
      });
      setSocket(newSocket);

      return () => {
        newSocket.disconnect();
        setSocket(null);
      };
    }
  }, [token]);

  // Set up Axios
  const axiosInstance = axios.create({
    baseURL: "http://127.0.0.1:5000",
    headers: {
      Authorization: token ? `Bearer ${token}` : "",
    },
  });

  // Login function
  const login = async (username: string, password: string) => {
    try {
      const response = await axiosInstance.post("/api/login", {
        username,
        password,
      });

      localStorage.setItem("token", response.data.token);
      setToken(response.data.token);
      setUser(response.data.username);
      setIsAuthenticated(true);
      axiosInstance.defaults.headers[
        "Authorization"
      ] = `Bearer ${response.data.token}`;
    } catch (error) {
      console.error("Login failed", error);
      throw new Error("Login failed");
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    if (socket) {
      socket.disconnect();
    }
    setSocket(null);
    axiosInstance.defaults.headers["Authorization"] = "";
  };

  // Verify authentication
  const checkAuth = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setIsAuthenticated(false);
      setToken(null);
      localStorage.removeItem("token");
      return;
    }

    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/verify`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.status === 200) {
        setIsAuthenticated(true);
        setToken(token);
        localStorage.setItem("token", response.data.token);
      } else {
        setIsAuthenticated(false);
        setToken(null);
        localStorage.removeItem("token");
      }
    } catch (error) {
      console.error("Auth check failed", error);
      setIsAuthenticated(false);
      setToken(null);
      localStorage.removeItem("token");
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, login, logout, user, token, socket }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
