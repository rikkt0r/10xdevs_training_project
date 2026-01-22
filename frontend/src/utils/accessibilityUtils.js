/**
 * Accessibility utility functions for WCAG 2.1 AA compliance
 */

/**
 * Generate a unique ID for form elements
 * Useful for connecting labels with inputs
 */
export const generateId = (prefix = 'element') => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Get ARIA role for button variants
 */
export const getButtonRole = (href) => {
  return href ? 'link' : 'button';
};

/**
 * Create accessible label for screen readers
 */
export const createAriaLabel = (label, description) => {
  return description ? `${label}, ${description}` : label;
};

/**
 * Check if element meets color contrast requirements (WCAG AA)
 * Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
 */
export const checkColorContrast = (foreground, background) => {
  const getLuminance = (color) => {
    const rgb = parseInt(color.substring(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = (rgb >> 0) & 0xff;

    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const l1 = getLuminance(foreground);
  const l2 = getLuminance(background);
  const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

  return {
    ratio: ratio.toFixed(2),
    passesAA: ratio >= 4.5,
    passesAALarge: ratio >= 3,
  };
};

/**
 * Focus trap utility for modals
 * Keeps focus within a container element
 */
export const createFocusTrap = (containerElement) => {
  const focusableElements = containerElement.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault();
      lastElement.focus();
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault();
      firstElement.focus();
    }
  };

  return {
    activate: () => {
      containerElement.addEventListener('keydown', handleTabKey);
      firstElement?.focus();
    },
    deactivate: () => {
      containerElement.removeEventListener('keydown', handleTabKey);
    },
  };
};

/**
 * Announce message to screen readers
 * Uses ARIA live region
 */
export const announceToScreenReader = (message, priority = 'polite') => {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

/**
 * Skip to main content link utility
 */
export const skipToContent = (targetId = 'main-content') => {
  const target = document.getElementById(targetId);
  if (target) {
    target.setAttribute('tabindex', '-1');
    target.focus();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

/**
 * Check if reduced motion is preferred
 */
export const prefersReducedMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Keyboard navigation helpers
 */
export const KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
};

/**
 * Handle keyboard interaction for custom interactive elements
 */
export const handleKeyboardClick = (event, callback) => {
  if (event.key === KEYS.ENTER || event.key === KEYS.SPACE) {
    event.preventDefault();
    callback(event);
  }
};

/**
 * WCAG 2.1 AA Accessibility Checklist
 *
 * PERCEIVABLE:
 * - [ ] All images have alt text
 * - [ ] Color is not the only means of conveying information
 * - [ ] Text has minimum 4.5:1 contrast ratio (3:1 for large text)
 * - [ ] Content is readable and functional at 200% zoom
 * - [ ] Audio/video have captions and transcripts
 *
 * OPERABLE:
 * - [ ] All functionality available via keyboard
 * - [ ] No keyboard traps
 * - [ ] Skip navigation links provided
 * - [ ] Focus indicators are visible (outline, border, etc.)
 * - [ ] Logical tab order
 * - [ ] No time limits or provide controls to extend/disable
 * - [ ] No content flashes more than 3 times per second
 *
 * UNDERSTANDABLE:
 * - [ ] Page language is identified (lang attribute)
 * - [ ] Navigation is consistent across pages
 * - [ ] Form labels and instructions are provided
 * - [ ] Error messages are clear and helpful
 * - [ ] Error prevention for critical actions (confirmations)
 *
 * ROBUST:
 * - [ ] Valid HTML (semantic elements)
 * - [ ] ARIA roles, states, and properties used correctly
 * - [ ] Compatible with assistive technologies
 * - [ ] Name, Role, Value available for all UI components
 */
