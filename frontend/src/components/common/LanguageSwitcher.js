import React from 'react';
import { Dropdown } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

/**
 * Language Switcher component
 * Dropdown for switching between EN/PL languages
 */
const LanguageSwitcher = ({ className = '' }) => {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'pl', label: 'Polski', flag: '🇵🇱' }
  ];

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (langCode) => {
    i18n.changeLanguage(langCode);
  };

  return (
    <Dropdown className={className}>
      <Dropdown.Toggle variant="outline-secondary" size="sm" id="language-dropdown">
        {currentLanguage.flag} {currentLanguage.label}
      </Dropdown.Toggle>

      <Dropdown.Menu>
        {languages.map(lang => (
          <Dropdown.Item
            key={lang.code}
            active={lang.code === i18n.language}
            onClick={() => handleLanguageChange(lang.code)}
          >
            {lang.flag} {lang.label}
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default LanguageSwitcher;
