# Frontend API Integration Contract

This document translates the repository-root `API.md` into frontend integration guidance. The root `API.md` remains canonical. If any discrepancy is found, do not silently create a new contract: coordinate with the backend owner and update the canonical documentation.

## Base URL and configuration

Use:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Create `frontend/.env.local` for local development; do not commit secrets. Add a safe placeholder to `.env.example` if the project uses one. Since this URL is public browser configuration, never put secrets in `NEXT_PUBLIC_*` variables.

The endpoint paths below are relative to the base URL, so do not prepend `/api/v1` a second time.

## Endpoints

| Purpose | Method and path | Body / parameters |
|---|---|---|
| Health | `GET /health` | None |
| Create/update profile | `POST /users/profile` | JSON `UserProfileInput` |
| Get profile | `GET /users/{user_id}` | Path ID |
| Add manual menu | `POST /menu/manual` | JSON `ManualMenuInput` |
| Upload PDF/image | `POST /menu/upload` | Multipart `file`, optional `restaurant_name` |
| Rank recommendations | `POST /recommendations/rank` | JSON `{ user_id, menu_id }` |
| Send feedback | `POST /feedback` | JSON `{ user_id, dish_id, liked, rating }` |

## Payloads and TypeScript types

Define types in one shared location, for example `frontend/src/types/api.ts`, adjusted to the existing project structure.

```ts
export type UserProfileInput = {
  name: string;
  budget: number;
  spice_tolerance: number; // validate 1–5
  health_goal: string;
  dietary_preferences: string[];
  allergies: string[];
  favorite_cuisines: string[];
  favorite_ingredients: string[];
};

export type UserProfile = UserProfileInput & {
  id: string;
  created_at?: string;
};

export type DishInput = {
  name: string;
  description: string;
  price: number;
  cuisine: string;
  ingredients: string[];
  diet_type: string;
  spice_level: number;
  health_tags: string[];
};

export type ManualMenuInput = {
  restaurant_name: string;
  dishes: DishInput[];
};

export type ManualMenuResult = {
  menu_id: string;
  restaurant_name: string;
  total_dishes_added: number;
  created_at?: string;
};

export type ExtractedDish = {
  id: string;
  name: string;
  price: number;
  cuisine: string;
  ingredients: string[];
  diet_type: string;
  spice_level: number;
  health_tags: string[];
};

export type MenuUploadResult = {
  menu_id: string;
  extracted_dishes_count: number;
  status: string;
  dishes: ExtractedDish[];
};

export type RecommendedDish = {
  dish_id: string;
  name: string;
  price: number;
  cuisine: string;
  match_score: number; // documented example uses 0–100
  compatibility_status: string;
  match_reasons: string[];
};

export type FilteredDish = {
  dish_id: string;
  name: string;
  price: number;
  compatibility_status: string;
  exclusion_reasons: string[];
};

export type RankingResult = {
  user_id: string;
  recommended_dishes: RecommendedDish[];
  filtered_dishes: FilteredDish[];
};

export type FeedbackInput = {
  user_id: string;
  dish_id: string;
  liked: boolean;
  rating: number; // integer 1–5
};

export type FeedbackResult = {
  feedback_id: string;
  status: string;
  message: string;
};

export type ApiError = {
  error?: {
    code?: string;
    message?: string;
    timestamp?: string;
  };
};
```

Important: treat these as the types implied by the current API examples, not proof that the backend has implemented every field exactly as written. Check actual Pydantic schemas/OpenAPI output when available and coordinate discrepancies with the backend owner.

## Request behavior

- JSON endpoints: use `JSON.stringify(payload)` and `Content-Type: application/json`.
- File upload: create `FormData`, append `file` and optional `restaurant_name`, and **do not manually set `Content-Type`**.
- Handle non-2xx HTTP responses as errors.
- Parse the documented `{ "error": { "code", "message", "timestamp" } }` shape defensively; the response may not always be valid JSON.
- Show an actionable message when the API is unreachable, e.g. “Cannot reach the backend. Check that FastAPI is running.”
- Never report success until the server returns a successful response.
- Do not log sensitive profile details unnecessarily.

## API client suggestion

Adapt to the existing frontend structure. A simple client can live at `src/lib/api-client.ts`:

```ts
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly code?: string,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  const isFormData =
    typeof FormData !== "undefined" && init.body instanceof FormData;

  if (init.body != null && !isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
    });
  } catch {
    throw new ApiRequestError(
      "Cannot reach the backend. Check that FastAPI is running.",
    );
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    let code: string | undefined;

    try {
      const body = (await response.json()) as {
        error?: { message?: string; code?: string };
        detail?: string;
      };
      message = body.error?.message ?? body.detail ?? message;
      code = body.error?.code;
    } catch {
      // Keep the HTTP status fallback if the response body is not JSON.
    }

    throw new ApiRequestError(message, response.status, code);
  }

  return (await response.json()) as T;
}
```

Adapt the snippet to project lint rules and TypeScript configuration. For requests with no body, do not add an unnecessary content-type header.

## Contract issues to verify with backend owner

1. **Health path:** the root API doc defines base URL `http://localhost:8000/api/v1` and endpoint `GET /health`; confirm FastAPI actually mounts this as `/api/v1/health`.
2. **Profile identity:** profile creation response uses an ID formatted like `u-...` while the prose calls it a UUID. Treat IDs as opaque strings unless backend schemas establish otherwise.
3. **Manual menu response:** the documented manual-menu response gives a `menu_id` and count but does not include dish IDs. The UI may need to rank using the returned `menu_id`; do not fabricate IDs.
4. **Ranking and complete menu:** response has `recommended_dishes` and `filtered_dishes`, but does not explicitly return compatible unranked dishes. To meet the product requirement that the complete menu stays visible, preserve the menu/upload response client-side and combine it with ranking results by stable dish ID. If backend IDs are not stable or manual-menu results omit dish records, ask the backend owner for a consistent response contract.
5. **Upload details:** upload response documents `id` on extracted dishes, while manual-menu example does not. Confirm actual behavior.
6. **Feedback semantics:** API example shows `liked` and `rating`, but not whether either can be omitted. Send both according to the current contract unless backend confirms optionality.
7. **CORS:** FastAPI must allow the local Next.js origin (commonly `http://localhost:3000`). If the browser reports CORS failure, report it to the backend owner; do not disable browser security.
8. **Validation:** the docs use `422` for schema errors and `400` for request validation. Handle both as user-correctable errors.

## Example calls

```ts
// Save profile
const profile = await apiRequest<UserProfile>("/users/profile", {
  method: "POST",
  body: JSON.stringify(profileInput),
});

// Get profile
const profile = await apiRequest<UserProfile>(
  `/users/${encodeURIComponent(userId)}`,
);

// Add manual menu
const menu = await apiRequest<ManualMenuResult>("/menu/manual", {
  method: "POST",
  body: JSON.stringify(menuInput),
});

// Upload menu
const form = new FormData();
form.append("file", file);
if (restaurantName.trim()) form.append("restaurant_name", restaurantName.trim());

const uploadResult = await apiRequest<MenuUploadResult>("/menu/upload", {
  method: "POST",
  body: form,
});

// Rank
const ranking = await apiRequest<RankingResult>("/recommendations/rank", {
  method: "POST",
  body: JSON.stringify({ user_id: userId, menu_id: menuId }),
});

// Feedback
const feedback = await apiRequest<FeedbackResult>("/feedback", {
  method: "POST",
  body: JSON.stringify({
    user_id: userId,
    dish_id: dishId,
    liked: true,
    rating: 5,
  }),
});
```
