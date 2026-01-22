/**
 * Ticket state constants
 */
export const TICKET_STATES = {
  NEW: 'new',
  IN_PROGRESS: 'in_progress',
  WAITING: 'waiting',
  RESOLVED: 'resolved',
  CLOSED: 'closed'
};

/**
 * Get Bootstrap badge variant for ticket state
 * @param {string} state - Ticket state
 * @returns {string} Bootstrap variant (primary, info, warning, success, secondary)
 */
export const getStateBadgeVariant = (state) => {
  const variants = {
    [TICKET_STATES.NEW]: 'primary',
    [TICKET_STATES.IN_PROGRESS]: 'info',
    [TICKET_STATES.WAITING]: 'warning',
    [TICKET_STATES.RESOLVED]: 'success',
    [TICKET_STATES.CLOSED]: 'secondary'
  };

  return variants[state] || 'secondary';
};

/**
 * Get human-readable label for ticket state
 * @param {string} state - Ticket state
 * @param {function} t - i18n translation function
 * @returns {string} Translated state label
 */
export const getStateLabel = (state, t) => {
  const labels = {
    [TICKET_STATES.NEW]: 'tickets.states.new',
    [TICKET_STATES.IN_PROGRESS]: 'tickets.states.inProgress',
    [TICKET_STATES.WAITING]: 'tickets.states.waiting',
    [TICKET_STATES.RESOLVED]: 'tickets.states.resolved',
    [TICKET_STATES.CLOSED]: 'tickets.states.closed'
  };

  return t(labels[state] || state);
};

/**
 * Get valid state transitions for a given state
 * @param {string} currentState - Current ticket state
 * @returns {string[]} Array of valid next states
 */
export const getValidTransitions = (currentState) => {
  const transitions = {
    [TICKET_STATES.NEW]: [
      TICKET_STATES.IN_PROGRESS,
      TICKET_STATES.WAITING,
      TICKET_STATES.CLOSED
    ],
    [TICKET_STATES.IN_PROGRESS]: [
      TICKET_STATES.WAITING,
      TICKET_STATES.RESOLVED,
      TICKET_STATES.CLOSED
    ],
    [TICKET_STATES.WAITING]: [
      TICKET_STATES.IN_PROGRESS,
      TICKET_STATES.RESOLVED,
      TICKET_STATES.CLOSED
    ],
    [TICKET_STATES.RESOLVED]: [
      TICKET_STATES.IN_PROGRESS,
      TICKET_STATES.CLOSED
    ],
    [TICKET_STATES.CLOSED]: [
      TICKET_STATES.IN_PROGRESS
    ]
  };

  return transitions[currentState] || [];
};

/**
 * Check if state transition is valid
 * @param {string} fromState - Current state
 * @param {string} toState - Target state
 * @returns {boolean}
 */
export const isValidTransition = (fromState, toState) => {
  return getValidTransitions(fromState).includes(toState);
};

/**
 * Get ticket source label
 * @param {string} source - Ticket source (email, external, form)
 * @param {function} t - i18n translation function
 * @returns {string} Translated source label
 */
export const getSourceLabel = (source, t) => {
  const labels = {
    email: 'tickets.sources.email',
    external: 'tickets.sources.external',
    form: 'tickets.sources.form'
  };

  return t(labels[source] || source);
};

/**
 * Get ticket source icon class
 * @param {string} source - Ticket source
 * @returns {string} Bootstrap icon class
 */
export const getSourceIcon = (source) => {
  const icons = {
    email: 'bi-envelope',
    external: 'bi-link-45deg',
    form: 'bi-file-text'
  };

  return icons[source] || 'bi-question-circle';
};
