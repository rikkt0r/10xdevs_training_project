/**
 * Timezone utility functions
 * Provides common timezone lists and helper functions
 */

/**
 * Get common IANA timezones grouped by region
 */
export const getTimezones = () => {
  return [
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'America/New York (EST/EDT)' },
    { value: 'America/Chicago', label: 'America/Chicago (CST/CDT)' },
    { value: 'America/Denver', label: 'America/Denver (MST/MDT)' },
    { value: 'America/Los_Angeles', label: 'America/Los Angeles (PST/PDT)' },
    { value: 'America/Toronto', label: 'America/Toronto (EST/EDT)' },
    { value: 'America/Vancouver', label: 'America/Vancouver (PST/PDT)' },
    { value: 'America/Sao_Paulo', label: 'America/São Paulo (BRT)' },
    { value: 'America/Buenos_Aires', label: 'America/Buenos Aires (ART)' },
    { value: 'America/Mexico_City', label: 'America/Mexico City (CST/CDT)' },
    { value: 'Europe/London', label: 'Europe/London (GMT/BST)' },
    { value: 'Europe/Paris', label: 'Europe/Paris (CET/CEST)' },
    { value: 'Europe/Berlin', label: 'Europe/Berlin (CET/CEST)' },
    { value: 'Europe/Rome', label: 'Europe/Rome (CET/CEST)' },
    { value: 'Europe/Madrid', label: 'Europe/Madrid (CET/CEST)' },
    { value: 'Europe/Warsaw', label: 'Europe/Warsaw (CET/CEST)' },
    { value: 'Europe/Moscow', label: 'Europe/Moscow (MSK)' },
    { value: 'Europe/Istanbul', label: 'Europe/Istanbul (TRT)' },
    { value: 'Europe/Athens', label: 'Europe/Athens (EET/EEST)' },
    { value: 'Asia/Dubai', label: 'Asia/Dubai (GST)' },
    { value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST)' },
    { value: 'Asia/Shanghai', label: 'Asia/Shanghai (CST)' },
    { value: 'Asia/Tokyo', label: 'Asia/Tokyo (JST)' },
    { value: 'Asia/Seoul', label: 'Asia/Seoul (KST)' },
    { value: 'Asia/Hong_Kong', label: 'Asia/Hong Kong (HKT)' },
    { value: 'Asia/Singapore', label: 'Asia/Singapore (SGT)' },
    { value: 'Asia/Bangkok', label: 'Asia/Bangkok (ICT)' },
    { value: 'Australia/Sydney', label: 'Australia/Sydney (AEDT/AEST)' },
    { value: 'Australia/Melbourne', label: 'Australia/Melbourne (AEDT/AEST)' },
    { value: 'Australia/Perth', label: 'Australia/Perth (AWST)' },
    { value: 'Pacific/Auckland', label: 'Pacific/Auckland (NZDT/NZST)' },
    { value: 'Pacific/Fiji', label: 'Pacific/Fiji (FJT)' },
  ];
};

/**
 * Get the browser's timezone
 */
export const getBrowserTimezone = () => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
};

/**
 * Format a date in a specific timezone
 * @param {Date|string} date - Date to format
 * @param {string} timezone - IANA timezone
 * @param {object} options - Intl.DateTimeFormat options
 */
export const formatInTimezone = (date, timezone, options = {}) => {
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  };

  return new Intl.DateTimeFormat('en-US', {
    ...defaultOptions,
    ...options,
    timeZone: timezone,
  }).format(new Date(date));
};
