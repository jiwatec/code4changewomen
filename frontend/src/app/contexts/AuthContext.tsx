import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { authAPI } from '../../services/api';

interface AuthContextType {
  isLoggedIn: boolean;
  userType: 'user' | 'volunteer' | 'admin' | null;
  userId: string | null;
  login: (type: 'user' | 'volunteer' | 'admin', phone: string, otp: string) => Promise<void>;
  logout: () => void;
  requestOtp: (phone: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
<<<<<<< HEAD
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userType, setUserType] = useState<'user' | 'volunteer' | 'admin' | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (type: 'user' | 'volunteer' | 'admin', phone: string, otp: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.verifyOtp(phone, otp) as { id: string };
      setIsLoggedIn(true);
      setUserType(type);
      setUserId(response.id);
      localStorage.setItem('userId', response.id);
      localStorage.setItem('userType', type);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const requestOtp = useCallback(async (phone: string) => {
    setLoading(true);
    setError(null);
    try {
      await authAPI.requestOtp(phone);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to request OTP');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
=======
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));
  const [userType, setUserType] = useState<'artisan' | 'validator' | null>(
    (localStorage.getItem('userType') as any) || null
  );

  const login = (type: 'artisan' | 'validator', token: string) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userType', type);
    setIsLoggedIn(true);
    setUserType(type);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userType');
>>>>>>> 1ecf60759c5880687b136805db2655f3eda0febb
    setIsLoggedIn(false);
    setUserType(null);
    setUserId(null);
    localStorage.removeItem('userId');
    localStorage.removeItem('userType');
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, userType, userId, login, logout, requestOtp, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
