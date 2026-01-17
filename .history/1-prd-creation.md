# PRD Creation Session - Simple Issue Tracker

**Date:** 2026-01-17

---

## Initial Requirements Summary

User provided the following initial requirements:

- You will be able to either track own tickets within this app or forward ticket creation (and then redirection) to other platform like Jira or Trello
- Users shall be divided into roles of "ticket board manager" (short: manager) and "typical user with no permissions" (short: user)
- Ticket can be created by multiple triggers: i.e. email, web view and mobile application
- Manager is able to create ticket boards and change ticket statuses on these boards
- Each board has an unique URL with a form for creating tickets
- Users will not be able to view full ticket board. Only his/her own ticket by unique URL
- Users is able to create ticket by sending email or web form or mobile application
- API provided by backend should be the same for web app and mobile app

### Additional Context

- The backend shall connect to email server SMTP and IMAP. For now, there will be only one inbox per manager (type of user), configured in his profile. This inbox will be used as ingress for tickets (created by mail) and egress for notifications
- Application will be divided into JavaScript single-page frontend and Python FastAPI backend
- Backend will be serving frontend from the same container, for now there won't be a separate CDN

---

## Q&A Session

### Round 1: Ticket Structure & Workflow

**Q1: What fields should a ticket contain?**
A: Title, description, state

**Q2: What ticket statuses should exist? Fixed set or customizable per board?**
A: Non-customizable at this stage. State transitions:
- Path A: new → in progress → (closed or rejected)
- Path B: new → rejected

**Q3: Can tickets be edited after creation? By whom?**
A: Ticket cannot be edited, only have their state changed

**Q4: Should tickets have a commenting/conversation thread?**
A: No

**Q5: Can managers assign tickets to other managers?**
A: No

### Round 1: External Platform Integration

**Q6: Is forwarding configured per-board or per-manager?**
A: Per board

**Q7: After forwarding, does the ticket remain viewable locally or redirect entirely?**
A: Fully redirected. Locally only a hook will exist, by which user and manager will be redirected to the ticket in the external platform

### Round 1: Access & Authentication

**Q8: How do users authenticate?**
A: Users are not authenticated. Only managers are. By email and password

**Q9: Does the user's unique ticket URL require login, or is it a "secret link"?**
A: It will be just a secret link. Whoever has the link, has access

**Q10: How are managers created?**
A: Self-registration

### Round 1: Email Flow Details

**Q11: How does the system identify which board an incoming email belongs to?**
A: Sender address (higher priority) and then by prefix. If neither matches, ticket shall be in the "standby queue" awaiting manager to assign it somewhere

**Q12: What notifications should be sent?**
A: Creation confirmation, on every status change. IMPORTANT: Status change may have additional comment provided by manager

### Round 1: Technical

**Q13: Database preference?**
A: PostgreSQL

**Q14: Expected scale?**
A: No real scale, it's a training project

**Q15: Any specific JS framework for the SPA?**
A: React

---

### Round 2: Standby Queue & Email

**Q1: Is the standby queue global or per-manager?**
A: Standby queue is per-manager. Again, inbox is configured per manager

**Q2: Can a manager configure multiple email addresses, or strictly one inbox?**
A: Can configure multiple and optionally assign them exclusively to chosen board

**Q3: Any specific format for subject prefix?**
A: Let's go with free-form. Matched by found keywords. Keyword will be configured per board. IMPORTANT: We need some kind of validation to ensure there will be no conflicts in keywords between boards.

### Round 2: User & Ticket Details

**Q4: How is the user's email captured for notifications?**
A: For web: dedicated form field, for app: either dedicated field or global app configuration, for email: sender address

**Q5: Can tickets have file attachments?**
A: No attachments whatsoever in this iteration

### Round 2: External Platform Integration

**Q6: Which platforms to support initially?**
A: Initially let's go with Jira and Trello

**Q7: One-way only, or should status changes sync back?**
A: Only one way

### Round 2: Frontend & Deployment

**Q8: Auth mechanism preference for managers?**
A: JWT token

**Q9: Deployment target?**
A: A self-contained Docker container will be initially hosted on DigitalOcean

### Round 2: Mobile App

**Q10: Is the mobile app in scope for this PRD?**
A: No. Just keep in mind, it will be here some day. And it should try to use the same API as web

### Round 2: Other

**Q11: Any spam prevention needed for public forms?**
A: Simple rate limiting in this iteration

**Q12: Multi-language support required?**
A: Yes, though translations should be kept on frontend side

---

### Round 3: Boards & Ownership

**Q1: Can multiple managers share/manage the same board?**
A: Boards are exclusive to single manager

**Q2: Can managers see each other's boards or tickets?**
A: Per manager (siloed)

### Round 3: Email Configuration

**Q3: When a manager has multiple inboxes and one is assigned exclusively to a board, what happens to emails arriving at non-exclusive inboxes?**
A: Keyword matching only on boards with no exclusivity

**Q4: How often should the system poll IMAP inboxes?**
A: Configurable as a choice: 1, 5 and 15 minutes

### Round 3: Keyword Conflict Validation

**Q5: Should conflicting keywords be blocked entirely or allowed with a warning?**
A: Hard validation

### Round 3: Ticket Links

**Q6: Do secret ticket links expire?**
A: They do not expire

### Round 3: External Platform Integration

**Q7: Where are Jira/Trello API credentials stored?**
A: Per board configuration

### Round 3: Web Form

**Q8: What fields on the public board form?**
A: Only: email, title, description

---

### Round 4: Manager Account & Profile

**Q1: What can managers configure in their profile?**
A: This will be enough (name, password, email inboxes, timezone)

**Q2: Password reset flow needed?**
A: Yes

**Q3: Can managers delete their account?**
A: No option for real deletion. Their account may be suspended, there will be no option to create further tickets (web form disabled and email replied to with information about suspension). Tickets should still be visible publicly

### Round 4: Board Lifecycle

**Q4: Can boards be archived or deleted?**
A: Deleted only when there are no tickets in state other than rejected - otherwise archived

**Q5: If deleted, what happens to existing tickets?**
A: Deleted

**Q6: Any other board settings?**
A: Greeting message for web form

### Round 4: Ticket Management for Managers

**Q7: Can managers delete tickets?**
A: No

**Q8: Should managers have search/filter capabilities?**
A: Yes, by title, state, date range, ticket contents (description)

**Q9: For tickets forwarded to external platforms, is the local stub kept indefinitely?**
A: Indefinitely

### Round 4: Notification Emails

**Q10: What should the "from" address be?**
A: Manager configured address

**Q11: Should notification emails include the secret ticket link?**
A: Yes

**Q12: Any branding/customization for email templates?**
A: Plain text for now

### Round 4: External Platform Integration

**Q13: For Jira: Cloud only, or also Server/Data Center?**
A: Cloud only

**Q14: What fields map to external platform?**
A: Title → Summary, Description → Description, plus additionally email address as a field if possible, else put it into description

**Q15: If external platform API fails during creation, what happens?**
A: Put it in manager's queue with other unassigned tickets. Manager may be able to either: retry or move ticket to board within app

### Round 4: Security & Error Handling

**Q16: Password requirements?**
A: Minimum 8 characters, no other requirements

**Q17: Rate limiting scope?**
A: Per IP, of course whitelist 127.0.0.1/localhost for testing purposes

**Q18: How to handle IMAP connection failures?**
A: Retry silently and log

---

### Round 5: Ordering & Pagination

**Q1: What fields can tickets be ordered by?**
A: Yes (date created, title, state, last updated)

**Q2: Default items per page?**
A: Yes (10, 25, 50 as options)

### Round 5: Manager Registration

**Q3: Email verification required during manager registration?**
A: Yes, by single use URL

**Q4: Any additional fields during registration?**
A: Email, password, name

### Round 5: Ticket Confirmation Emails

**Q5: What should the confirmation email include?**
A: Yes (ticket title, description, secret link, board name)

### Round 5: Technical Specifics

**Q6: Python version preference?**
A: 3.12

**Q7: Node version for frontend build?**
A: 22

**Q8: ORM preference?**
A: SQLAlchemy

**Q9: Database migration tool?**
A: Alembic

**Q10: Logging format?**
A: GELF format

**Q11: Health check endpoint needed?**
A: Yes. Create "/health" endpoint. No rate limiting there.

### Round 5: Security

**Q12: CORS policy?**
A: Yes (same-origin since frontend served from same container)

**Q13: Any specific security headers required?**
A: Prevent frame clickjacking, add some best-practice headers. CSP is not needed

### Round 5: UX Details

**Q14: Should manager dashboard be responsive/mobile-friendly?**
A: Responsive

**Q15: Form validation feedback style?**
A: Inline errors

---

### Round 6: Connection Testing

**Q1: Should there be a "test connection" button for Jira/Trello configuration?**
A: Yes

**Q2: Same for IMAP/SMTP inbox configuration?**
A: Yes

### Round 6: UI Flows

**Q3: How does a manager change ticket state?**
A: Dropdown on ticket board or button on ticket details

**Q4: Board deletion - any confirmation flow?**
A: Simple modal to confirm deletion

**Q5: Account suspension - confirmation flow?**
A: Require password and additional confirmation modal "are you sure"

### Round 6: External Ticket Redirect

**Q6: When a ticket is forwarded to Jira/Trello, what's stored locally?**
A: Creation date, title, sender email and external URL

### Round 6: Translations

**Q7: How are translations stored?**
A: Yes (JSON files per language in frontend)

### Round 6: Email Inbox Polling

**Q8: Should polling be per-inbox or global setting?**
A: Per inbox

---

## Post-Draft Revisions

### Revision 1: Suspension Message Display
- The same suspension message (as for email) should be visible over disabled forms

### Revision 2: Suspension Message Configuration
- Suspension message should ONLY be available for configuration during suspension process (not in profile settings)

### Revision 3: Ticket Creation Form URL
- Ticket creation form should be available on unique URL in form of `/board/{unique-name}`

### Revision 4: Data Model Updates
- ExternalTicket "uuid field" should check whether Ticket with the same UUID doesn't exist and optionally retry with another UUID
- Ticket should have "updated_at" field which will reflect last status change

### Revision 5: Out of Scope Clarification
- "Ticket comments/conversation threads" is incorrect - ticket CAN have optional comments by manager provided on status change
- Changed to: "Ticket conversation threads (note: single manager comment on status change IS in scope)"

### Revision 6: Missing Data Model
- Added TicketStatusChange table: id, ticket_id, previous_state, new_state, comment (optional), created_at

---

## Output

PRD document created at: `docs/PRD.md`
