import { formatDistanceToNow, format, parseISO } from 'date-fns';
import { enUS, pl } from 'date-fns/locale';

const locales = { en: enUS, pl };

/**
 * Get date-fns locale based on i18n language
 */
export const getDateLocale = (language = 'en') => {
  return locales[language] || enUS;
};

/**
 * Format a date string to a readable format
 * @param {string|Date} date - ISO date string or Date object
 * @param {string} formatStr - date-fns format string (default: 'PPP')
 * @param {string} language - Language code for locale
 * @returns {string} Formatted date string
 */
export const formatDate = (date, formatStr = 'PPP', language = 'en') => {
  if (!date) return '';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, formatStr, { locale: getDateLocale(language) });
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
};

/**
 * Format date with time
 * @param {string|Date} date - ISO date string or Date object
 * @param {string} language - Language code for locale
 * @returns {string} Formatted date and time string
 */
export const formatDateTime = (date, language = 'en') => {
  return formatDate(date, 'PPp', language);
};

/**
 * Format date relative to now (e.g., "2 hours ago", "3 days ago")
 * @param {string|Date} date - ISO date string or Date object
 * @param {string} language - Language code for locale
 * @returns {string} Relative time string
 */
export const formatRelativeDate = (date, language = 'en') => {
  if (!date) return '';

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return formatDistanceToNow(dateObj, {
      addSuffix: true,
      locale: getDateLocale(language)
    });
  } catch (error) {
    console.error('Error formatting relative date:', error);
    return '';
  }
};

/**
 * Format date for display in short format (e.g., "Jan 22, 2026")
 * @param {string|Date} date - ISO date string or Date object
 * @param {string} language - Language code for locale
 * @returns {string} Short date string
 */
export const formatShortDate = (date, language = 'en') => {
  return formatDate(date, 'PP', language);
};

/**
 * Check if a date is today
 * @param {string|Date} date - ISO date string or Date object
 * @returns {boolean}
 */
export const isToday = (date) => {
  if (!date) return false;

  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    const today = new Date();
    return (
      dateObj.getDate() === today.getDate() &&
      dateObj.getMonth() === today.getMonth() &&
      dateObj.getFullYear() === today.getFullYear()
    );
  } catch (error) {
    return false;
  }
};
