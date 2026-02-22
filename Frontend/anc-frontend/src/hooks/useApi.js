import { useState, useCallback } from 'react';

export function useApi(fn) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fn(...args);
      setData(result);
      return result;
    } catch (e) {
      const msg = e.response?.data?.message || e.message || 'Request failed';
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [fn]);

  return { data, loading, error, run, setData };
}
