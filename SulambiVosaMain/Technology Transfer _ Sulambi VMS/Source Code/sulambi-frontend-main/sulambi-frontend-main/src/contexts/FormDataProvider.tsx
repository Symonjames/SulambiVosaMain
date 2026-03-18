import { createContext, ReactNode, useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { produce } from "immer";
import {
  getFromSessionObfuscated,
  saveToSessionObfuscated,
} from "../utils/storage";

// Check if we're in browser environment (sessionStorage available)
const isBrowser = typeof window !== 'undefined' && typeof sessionStorage !== 'undefined';

interface Triplets {
  formData: any;
  setFormData: (value: any) => void;
  immutableSetFormData: (immutableVal: any) => void;
  mutableSetFormData: (mutableVal: any) => void;
  resetFormData: () => void;
  // New: Page-specific form data methods
  getPageFormData: (pagePath?: string) => any;
  setPageFormData: (pagePath: string, data: any) => void;
}

export const FormDataContext = createContext<Triplets>({
  formData: {},
  setFormData: () => {},
  immutableSetFormData: () => {},
  mutableSetFormData: () => {},
  resetFormData: () => {},
  getPageFormData: () => ({}),
  setPageFormData: () => {},
});

const FormDataProvider = ({ children }: { children: ReactNode }) => {
  // Safely use useLocation - will be available when inside BrowserRouter
  let location;
  try {
    location = useLocation();
  } catch (error) {
    // Fallback if not inside BrowserRouter (shouldn't happen, but safety check)
    location = { pathname: window?.location?.pathname || '/' };
  }

  // Global form data — sessionStorage + obfuscated so it's not plain text in Application tab
  const [formData, setFormData] = useState(() => {
    if (!isBrowser) return {};
    try {
      let saved = getFromSessionObfuscated<Record<string, any>>('formData', null);
      if (saved && typeof saved === 'object') return saved;
      const legacy = localStorage.getItem('formData');
      if (legacy) {
        try {
          saved = JSON.parse(legacy) as Record<string, any>;
          if (saved && typeof saved === 'object') return saved;
        } catch (_) {}
      }
      return {};
    } catch (error) {
      console.error('Error loading form data from storage:', error);
      return {};
    }
  });

  // Page-specific form data — sessionStorage + obfuscated
  const [pageFormData, setPageFormData] = useState<Record<string, any>>(() => {
    if (!isBrowser) return {};
    try {
      let saved = getFromSessionObfuscated<Record<string, any>>('pageFormData', null);
      if (saved && typeof saved === 'object') return saved;
      const legacy = localStorage.getItem('pageFormData');
      if (legacy) {
        try {
          saved = JSON.parse(legacy) as Record<string, any>;
          if (saved && typeof saved === 'object') return saved;
        } catch (_) {}
      }
      return {};
    } catch (error) {
      console.error('Error loading page form data from storage:', error);
      return {};
    }
  });

  // One-time: remove old plain-text form data from localStorage (migrate to session + obfuscated)
  useEffect(() => {
    if (!isBrowser) return;
    try {
      localStorage.removeItem('formData');
      localStorage.removeItem('pageFormData');
    } catch (_) {}
  }, []);

  // Load form data for current page when navigating
  useEffect(() => {
    try {
      const pageData = pageFormData[location.pathname];
      if (pageData) {
        // Merge page-specific data with global data
        setFormData((prev) => ({ ...prev, ...pageData }));
      }
    } catch (error) {
      console.error('Error loading page form data:', error);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  // Save global form data to sessionStorage (obfuscated) whenever it changes
  useEffect(() => {
    if (!isBrowser) return;
    try {
      if (Object.keys(formData).length > 0) {
        saveToSessionObfuscated('formData', formData);
        if (location?.pathname) {
          const updated = {
            ...pageFormData,
            [location.pathname]: formData,
          };
          setPageFormData(updated);
          saveToSessionObfuscated('pageFormData', updated);
        }
      }
    } catch (error) {
      console.error('Error saving form data to storage:', error);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData]);

  const immutableSetFormData = (immutableVal: any) => {
    setFormData((prevData) =>
      produce(prevData, (draft) => {
        Object.assign(draft, immutableVal);
      })
    );
  };

  const mutableSetFormData = (immutableVal: any) => {
    setFormData((prevData) => ({ ...prevData, ...immutableVal }));
  };

  const resetFormData = () => {
    setFormData({});
    if (isBrowser && location?.pathname) {
      const updated = { ...pageFormData };
      delete updated[location.pathname];
      setPageFormData(updated);
      saveToSessionObfuscated('pageFormData', updated);
    }
  };

  const getPageFormData = (pagePath?: string) => {
    if (!isBrowser) return {};
    const path = pagePath || location?.pathname || '/';
    return pageFormData[path] || {};
  };

  const setPageFormDataForPath = (pagePath: string, data: any) => {
    if (!isBrowser) return;
    const updated = {
      ...pageFormData,
      [pagePath]: data,
    };
    setPageFormData(updated);
    saveToSessionObfuscated('pageFormData', updated);

    if (pagePath === location?.pathname) {
      setFormData(data);
    }
  };

  return (
    <FormDataContext.Provider
      value={{
        formData,
        setFormData,
        immutableSetFormData,
        mutableSetFormData,
        resetFormData,
        getPageFormData,
        setPageFormData: setPageFormDataForPath,
      }}
    >
      {children}
    </FormDataContext.Provider>
  );
};

export default FormDataProvider;
