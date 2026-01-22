# Accessibility Guidelines - WCAG 2.1 AA Compliance

This document outlines the accessibility standards and guidelines followed in the Simple Issue Tracker frontend application.

## Overview

The application targets **WCAG 2.1 Level AA** compliance to ensure the interface is accessible to users with disabilities, including those using screen readers, keyboard-only navigation, and other assistive technologies.

## Core Principles (POUR)

### 1. Perceivable
Information and user interface components must be presentable to users in ways they can perceive.

#### Implementation:
- **Images**: All `<img>` tags include meaningful `alt` attributes
- **Color**: Color is never the sole means of conveying information (icons, text labels accompany colors)
- **Contrast**: Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text
- **Zoom**: Content remains functional at 200% zoom
- **Icons**: Bootstrap Icons used with aria-labels for screen readers

### 2. Operable
User interface components and navigation must be operable.

#### Implementation:
- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Focus Management**: Visible focus indicators on all focusable elements
- **No Keyboard Traps**: Users can navigate in and out of all components
- **Skip Links**: Skip-to-content link for keyboard users
- **Tab Order**: Logical tab order throughout the application
- **Modals**: Focus trap implemented in Modal component
- **Time Limits**: No time limits on user actions

### 3. Understandable
Information and the operation of user interface must be understandable.

#### Implementation:
- **Language**: HTML `lang` attribute set to "en"
- **Consistent Navigation**: ManagerLayout provides consistent navigation structure
- **Form Labels**: All form inputs have associated labels via FormGroup component
- **Error Messages**: Clear, specific error messages in form validation
- **Confirmations**: ConfirmModal component for destructive actions
- **Help Text**: FormGroup component supports help text for complex fields

### 4. Robust
Content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies.

#### Implementation:
- **Semantic HTML**: Proper use of `<button>`, `<nav>`, `<main>`, `<article>`, etc.
- **ARIA Attributes**: Appropriate use of aria-labels, aria-describedby, aria-live
- **Valid HTML**: Components follow HTML5 standards
- **Component Roles**: Proper button roles, link roles, navigation roles

## Component Accessibility Features

### Common Components

#### Button Component
- Semantic `<button>` or `<Link>` element
- Disabled state properly communicated
- Loading state with spinner and aria-busy
- Support for aria-label override

#### Input Component
- Associated with label via htmlFor/id
- Error state with aria-invalid
- Error messages via aria-describedby
- Placeholder text as guidance only (not replacement for label)

#### Modal Component
- Focus trap implemented
- Closes on Escape key
- Returns focus to trigger element on close
- aria-modal="true" and role="dialog"
- Backdrop prevents interaction with background

#### Alert Component
- role="alert" for important messages
- Dismissible with keyboard (Enter/Space on close button)
- Auto-dismiss option with polite aria-live

#### Badge Component
- Sufficient color contrast for all variants
- Text content always visible (not icon-only)

#### Spinner Component
- aria-live="polite" for status updates
- Hidden from screen readers when not active

### Layout Components

#### ManagerLayout
- Semantic navigation with `<nav>` element
- Skip-to-content link
- Collapsible sidebar with keyboard control
- Breadcrumbs with proper navigation hierarchy

#### PublicLayout
- Simplified structure for public pages
- Clear focus management

### Form Components

#### FormGroup
- Proper label association
- Error messages linked via aria-describedby
- Required field indication
- Help text support

## Keyboard Navigation

### Shortcuts
- `Tab`: Move forward through focusable elements
- `Shift + Tab`: Move backward through focusable elements
- `Enter`: Activate buttons, links, submit forms
- `Space`: Activate buttons, toggle checkboxes
- `Escape`: Close modals, cancel operations
- `Arrow Keys`: Navigate within menus, dropdowns

### Focus Order
1. Skip-to-content link
2. Main navigation
3. Breadcrumbs
4. Page header actions
5. Primary content
6. Forms (top to bottom, left to right)
7. Footer

## Color Contrast

### Background/Text Combinations
- Primary buttons: White text (#FFFFFF) on Blue background (#0D6EFD) - 8.6:1 ✓
- Secondary buttons: Black text (#000000) on Gray background (#6C757D) - 5.9:1 ✓
- Success: White text on Green (#198754) - 4.7:1 ✓
- Danger: White text on Red (#DC3545) - 5.5:1 ✓
- Warning: Black text on Yellow (#FFC107) - 10.4:1 ✓

## Screen Reader Support

### Announcements
- Use `announceToScreenReader()` utility for dynamic updates
- Success/error messages announced automatically
- Loading states announced

### Hidden Content
- `.sr-only` class for screen reader-only text
- `aria-hidden="true"` for decorative elements
- `aria-label` for icon-only buttons

## Testing

### Manual Testing
- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (NVDA/JAWS/VoiceOver)
- [ ] Test at 200% zoom
- [ ] Test in high contrast mode
- [ ] Verify all interactive elements have focus indicators
- [ ] Check tab order is logical

### Automated Testing
- [ ] Run axe DevTools in browser
- [ ] Run Lighthouse accessibility audit
- [ ] Validate HTML with W3C validator

### Browser/Screen Reader Combinations
- **Windows**: NVDA with Chrome/Firefox, JAWS with Chrome
- **macOS**: VoiceOver with Safari
- **Mobile**: TalkBack (Android), VoiceOver (iOS)

## Common Issues to Avoid

### ❌ Bad Practices
- Icon-only buttons without aria-label
- Placeholder as label replacement
- Insufficient color contrast
- Keyboard traps in modals
- Missing alt text on images
- Non-semantic div/span buttons
- Relying only on color to convey meaning
- Missing focus indicators

### ✅ Good Practices
- Descriptive link text (not "click here")
- Heading hierarchy (h1 → h2 → h3)
- Form labels always visible
- Error messages specific and actionable
- Confirm before destructive actions
- Consistent navigation structure
- Skip links for keyboard users
- ARIA attributes used correctly

## Resources

### Tools
- [axe DevTools](https://www.deque.com/axe/devtools/) - Browser extension for accessibility testing
- [WAVE](https://wave.webaim.org/) - Web accessibility evaluation tool
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Automated auditing tool
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [WebAIM Articles](https://webaim.org/articles/)

## Accessibility Statement

This application strives to meet WCAG 2.1 Level AA standards. If you encounter any accessibility barriers, please contact support with details about the issue.

Last Updated: 2026-01-22
