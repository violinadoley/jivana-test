"use client";

import {
  User,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  GoogleAuthProvider,
} from "firebase/auth";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { setAuthTokenProvider } from "@/lib/api";
import { getFirebaseAuth, isFirebaseConfigured } from "@/lib/firebase/client";
import {
  identifyPostHogUser,
  resetPostHogUser,
} from "@/lib/posthog/client";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  configured: boolean;
  authRequired: boolean;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const configured = isFirebaseConfigured();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(configured);
  const authRequired =
    process.env.NEXT_PUBLIC_AUTH_REQUIRED === "true";

  useEffect(() => {
    const auth = getFirebaseAuth();
    if (!auth) {
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (nextUser) => {
      setUser(nextUser);
      setLoading(false);
      if (nextUser?.uid) {
        identifyPostHogUser(nextUser.uid);
      } else {
        resetPostHogUser();
      }
    });
    return () => unsubscribe();
  }, [configured]);

  useEffect(() => {
    setAuthTokenProvider(async () => {
      const auth = getFirebaseAuth();
      if (!auth?.currentUser) {
        return null;
      }
      return auth.currentUser.getIdToken();
    });
    return () => setAuthTokenProvider(null);
  }, []);

  const loginWithGoogle = useCallback(async () => {
    const auth = getFirebaseAuth();
    if (!auth) {
      throw new Error(
        "Firebase is not configured. Add NEXT_PUBLIC_FIREBASE_* variables."
      );
    }
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
  }, []);

  const logout = useCallback(async () => {
    const auth = getFirebaseAuth();
    if (auth) {
      await signOut(auth);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      configured,
      authRequired,
      loginWithGoogle,
      logout,
    }),
    [user, loading, configured, authRequired, loginWithGoogle, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
