# Frontend UI Requirements

## UX principles

- Make the menu useful first; personalization is an enhancement, not a replacement.
- Explain recommendations in plain language using the backend's match reasons.
- Clearly distinguish preference match from dietary/allergy safety.
- Keep the MVP usable without a paid API or frontend AI calls.
- Use the backend for filtering and ranking. The frontend only collects inputs and presents results.

## MVP screens

### 1. Menu and home view

- Show restaurant name and menu context.
- Provide a clear action to add a menu manually or upload a PDF/image.
- Show a preference setup/edit action.
- Once a menu is available, render the entire menu.
- Provide tabs/sections/filters such as:
  - Recommended for you
  - Other menu items
  - Incompatible / needs verification
- Do not delete dishes from the client-side menu when ranking is run.

### 2. Preference form

Fields:
- Name
- Budget (non-negative number; currency displayed consistently as INR/₹ for the project)
- Spice tolerance (1–5)
- Health goal
- Dietary preferences (multi-select)
- Allergies (multi-value input)
- Favorite cuisines (multi-value input)
- Favorite ingredients (multi-value input)

Validation:
- Budget must be finite and non-negative.
- Spice tolerance must be an integer from 1 through 5.
- Trim strings and remove empty entries from list inputs.
- Do not assume that an unselected allergy means no allergies unless the user confirms it.
- Preserve the form values when a request fails.

### 3. Menu entry/upload

Manual entry fields per dish:
- Name
- Description
- Price
- Cuisine
- Ingredients
- Diet type
- Spice level
- Health tags

Upload:
- Accept PDF and common image formats supported by backend.
- Validate file presence and reasonable size client-side, without pretending this guarantees backend acceptance.
- Show uploading, parsed result, error, and retry states.
- Show extracted count and allow users to review returned dish data if practical.

### 4. Recommendation result cards

Each recommended card should display:
- Dish name
- Price
- Cuisine
- Match score as a percentage (only if backend returns a valid score)
- Backend-provided match reasons
- Feedback controls

For filtered dishes:
- Display an explicit “Incompatible” or “Needs verification” status as appropriate.
- Display backend-provided exclusion reasons.
- Never show a filtered dish as recommended.
- Do not infer safety from incomplete ingredient data.

### 5. Feedback

- Allow like/dislike and a 1–5 rating.
- Show pending and success/failure states.
- Prevent accidental repeated submissions while a request is in progress.
- Keep the UI honest: success only after a successful API response.

## Visual guidance

Use a clean, modern, food-focused interface with warm neutral surfaces and one restrained accent color. Favor readable typography, generous spacing, strong hierarchy, and clear dish cards over excessive animations or glassmorphism.

Responsive behavior:
- Mobile: single-column dish cards and full-width forms.
- Tablet: flexible two-column layouts where useful.
- Desktop: readable content width; use side-by-side menu/preferences only when it improves workflow.

Accessibility:
- Use proper labels for all form controls.
- Ensure keyboard operation and visible focus.
- Use text and icons in addition to color for compatibility status.
- Announce important errors/status changes accessibly.
- Respect reduced-motion preferences if animation is used.

## Explicitly out of MVP scope

Unless the project owner approves a change, do not implement:
- Payment or checkout
- Restaurant staff/admin dashboard
- Authentication system
- Real-time collaborative menu editing
- A chatbot that decides recommendations
- Frontend-based AI scoring or allergy decisions
- Collaborative filtering or advanced ML
- QR scanning as a separate device capability
- Mobile native application
