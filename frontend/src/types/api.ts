export type UserProfileInput = {
  name: string;
  budget: number;
  spice_tolerance: number; // integer 1–5
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
  match_score: number; // 0-100%
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
  rating: number; // 1-5
};

export type FeedbackResult = {
  feedback_id: string;
  status: string;
  message: string;
};

export type HealthStatus = {
  status: string;
  version: string;
  recommender_engine?: string;
};

export type UnifiedDish = {
  id: string;
  name: string;
  description?: string;
  price: number;
  cuisine: string;
  ingredients: string[];
  diet_type: string;
  spice_level: number;
  health_tags: string[];
  // Ranking fields when available
  match_score?: number;
  compatibility_status?: 'RECOMMENDED' | 'COMPATIBLE' | 'FILTERED' | 'UNRANKED';
  match_reasons?: string[];
  exclusion_reasons?: string[];
};
