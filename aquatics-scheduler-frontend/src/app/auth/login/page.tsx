// src/app/auth/login/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../../lib/firebase';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push('/dashboard'); // Redirect to dashboard on successful login
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background dark:bg-dark-background">
      <div className="p-8 rounded-lg shadow-md w-full max-w-md bg-neutral-light dark:bg-dark-neutral-light">
        <h2 className="text-2xl font-bold text-primary dark:text-dark-primary mb-6 text-center">Login</h2>
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label htmlFor="email" className="block text-neutral-dark dark:text-dark-neutral-dark text-sm font-bold mb-2">Email:</label>
            <input
              type="email"
              id="email"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-neutral-dark dark:text-dark-neutral-dark leading-tight focus:outline-none focus:shadow-outline bg-neutral dark:bg-dark-neutral"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-neutral-dark dark:text-dark-neutral-dark text-sm font-bold mb-2">Password:</label>
            <input
              type="password"
              id="password"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-neutral-dark dark:text-dark-neutral-dark leading-tight focus:outline-none focus:shadow-outline bg-neutral dark:bg-dark-neutral"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-red-500 text-xs italic mb-4">{error}</p>}
          <div className="flex items-center justify-between">
            <button
              type="submit"
              className="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Sign In
            </button>
            <a
              href="/auth/register"
              className="inline-block align-baseline font-bold text-sm text-primary hover:text-primary-dark"
            >
              Don't have an account? Register
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}
