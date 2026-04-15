import axios from "./init";
import { API_BASE_URL } from "./init";

// Analytics API functions
export const getEventSuccessAnalytics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/event-success`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching event success analytics:', error);
    throw error;
  }
};

/** Volunteer dropout analytics — uses axios + relative URL so session cookie is sent (same as satisfaction/dashboard). */
export const getVolunteerDropoutAnalytics = async () => {
  try {
    const response = await axios.get("/analytics/volunteer-dropout");
    return response.data;
  } catch (error: any) {
    console.error('Error fetching volunteer dropout analytics:', error);
    const message = error.response?.data?.message || error.message || 'Failed to fetch volunteer dropout analytics.';
    throw new Error(message);
  }
};

export const getPredictiveInsights = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/insights`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching predictive insights:', error);
    throw error;
  }
};

export const getAllAnalytics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/all`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching all analytics:', error);
    throw error;
  }
};

// Enhanced analytics for satisfaction ratings
export const getSatisfactionAnalytics = async (year?: string) => {
  try {
    const url = year 
      ? `/analytics/satisfaction?year=${year}`
      : `/analytics/satisfaction`;
      
    // Use axios instead of fetch for consistency with other API calls
    const response = await axios.get(url);
    return response;
  } catch (error) {
    console.error('Error fetching satisfaction analytics:', error);
    throw error;
  }
};

// Get satisfaction analytics for a specific event
export const getEventSatisfactionAnalytics = async (eventId: number, eventType: string) => {
  try {
    const url = `${API_BASE_URL}/analytics/satisfaction/event?eventId=${eventId}&eventType=${eventType}`;
      
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching event satisfaction analytics:', error);
    throw error;
  }
};

// Rebuild pre-aggregated semester satisfaction (admin)
export const rebuildSatisfactionAnalytics = async (year?: string) => {
  try {
    const url = year
      ? `${API_BASE_URL}/analytics/satisfaction/rebuild?year=${encodeURIComponent(year)}`
      : `${API_BASE_URL}/analytics/satisfaction/rebuild`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Rebuild failed: ${response.status} ${text}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error rebuilding satisfaction analytics:', error);
    throw error;
  }
};

// Seed demo satisfaction surveys (admin/officer) so predictive ratings has real DB-backed values
export const seedSatisfactionDemoData = async (count: number = 80) => {
  try {
    const response = await axios.get(`/analytics/dev/seed?count=${count}`);
    const data = response.data;
    if (!data?.success) {
      console.warn(
        "[seedSatisfactionDemoData] Backend reported success=false:",
        data?.message || data
      );
    }
    return data;
  } catch (error) {
    console.error("Error seeding satisfaction demo data:", error);
    throw error;
  }
};

/** Dropout risk analytics — uses axios + relative URL so session cookie is sent (same as satisfaction/dashboard). */
export const getDropoutRiskAnalytics = async (year?: string) => {
  try {
    const url = year
      ? `/analytics/volunteer-dropout?year=${year}`
      : "/analytics/volunteer-dropout";

    const response = await axios.get(url);
    return response.data;
  } catch (error: any) {
    console.error('[DROPOUT API] Error fetching dropout risk analytics:', error);
    const message = error.response?.data?.message || error.message || 'Failed to fetch dropout risk analytics.';
    return {
      success: false,
      error: message,
      message,
      data: { semesterData: [], atRiskVolunteers: [] }
    };
  }
};

// Clear all analytics data (requirements and evaluations)
export const clearAnalyticsData = async () => {
  try {
    const axios = (await import('axios')).default;
    const response = await axios.post(`/analytics/dev/clear`, {}, {
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });
    
    return response.data;
  } catch (error: any) {
    console.error('Error clearing analytics data:', error);
    // Don't throw error - fail silently for automatic clearing
    return { success: false, message: 'Failed to clear analytics data' };
  }
};
