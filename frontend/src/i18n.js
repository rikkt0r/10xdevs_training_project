import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from './locales/en.json';
import plTranslations from './locales/pl.json';

const resources = {
  en: {
    translation: enTranslations,
  },
  pl: {
    translation: plTranslations,
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: process.env.REACT_APP_DEFAULT_LOCALE || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
