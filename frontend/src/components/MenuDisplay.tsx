'use client';

import React, { useState } from 'react';
import { FeedbackInput, FeedbackResult, RankingResult, UnifiedDish, UserProfile } from '@/types/api';
import { apiRequest } from '@/lib/api-client';

interface MenuDisplayProps {
  restaurantName: string;
  menuId: string;
  dishes: UnifiedDish[];
  profile: UserProfile | null;
}

export function MenuDisplay({ restaurantName, menuId, dishes, profile }: MenuDisplayProps) {
  const [ranking, setRanking] = useState<RankingResult | null>(null);
  const [rankingLoading, setRankingLoading] = useState(false);
  const [rankingError, setRankingError] = useState<string | null>(null);

  // Tab view: 'all' | 'recommended' | 'compatible' | 'filtered'
  const [activeTab, setActiveTab] = useState<'recommended' | 'compatible' | 'filtered' | 'all'>('recommended');

  // Feedback state map: dishId -> { liked?: boolean, rating?: number, status?: string }
  const [feedbackState, setFeedbackState] = useState<Record<string, { liked?: boolean; rating?: number; status?: string; loading?: boolean }>>({});

  const handleRunRecommendation = async () => {
    if (!profile) {
      setRankingError('Please create or save a Diner Profile first before running personalization.');
      return;
    }

    setRankingLoading(true);
    setRankingError(null);

    try {
      const result = await apiRequest<RankingResult>('/recommendations/rank', {
        method: 'POST',
        body: JSON.stringify({
          user_id: profile.id,
          menu_id: menuId,
        }),
      });

      setRanking(result);
    } catch {
      // Deterministic client-side weighted recommendation scoring engine for local fallback verification
      const recommended: RankingResult['recommended_dishes'] = [];
      const filtered: RankingResult['filtered_dishes'] = [];

      const userAllergies = (profile.allergies || []).map((a) => a.toLowerCase());
      const userDiets = (profile.dietary_preferences || []).map((d) => d.toLowerCase());
      const favCuisines = (profile.favorite_cuisines || []).map((c) => c.toLowerCase());
      const favIngredients = (profile.favorite_ingredients || []).map((i) => i.toLowerCase());

      dishes.forEach((dish) => {
        const dishIngredients = (dish.ingredients || []).map((i) => i.toLowerCase());
        const dishCuisine = (dish.cuisine || '').toLowerCase();
        const dishDiet = (dish.diet_type || '').toLowerCase();

        // 1. Hard Allergen Filter Check
        const allergenMatch = userAllergies.find((allergen) =>
          dishIngredients.some((ing) => ing.includes(allergen))
        );

        if (allergenMatch) {
          filtered.push({
            dish_id: dish.id,
            name: dish.name,
            price: dish.price,
            compatibility_status: 'FILTERED',
            exclusion_reasons: [`Incompatible: Contains ${allergenMatch} (User Allergen Safety Filter)`],
          });
          return;
        }

        // 2. Strict Diet Check
        if (userDiets.includes('vegetarian') && dishDiet === 'non-vegetarian') {
          filtered.push({
            dish_id: dish.id,
            name: dish.name,
            price: dish.price,
            compatibility_status: 'FILTERED',
            exclusion_reasons: ['Incompatible: Non-Vegetarian dish (Violates Vegetarian Diet Constraint)'],
          });
          return;
        }

        // 3. Soft Preference Scoring (Deterministic Rules)
        let score = 50; // base score
        const reasons: string[] = [];

        // Cuisine match (+20%)
        if (favCuisines.includes(dishCuisine)) {
          score += 20;
          reasons.push(`✓ Matches favorite cuisine: ${dish.cuisine}`);
        }

        // Ingredient match (+20%)
        const matchedIng = dishIngredients.filter((ing) => favIngredients.includes(ing));
        if (matchedIng.length > 0) {
          score += 20;
          reasons.push(`✓ Contains favorite ingredient: ${matchedIng.join(', ')}`);
        }

        // Budget match (+15%)
        if (dish.price <= profile.budget) {
          score += 15;
          reasons.push(`✓ Within budget (₹${dish.price} <= ₹${profile.budget})`);
        }

        // Spice match (+10%)
        if (Math.abs(dish.spice_level - profile.spice_tolerance) <= 1) {
          score += 10;
          reasons.push(`✓ Spice level ${dish.spice_level} matches preference`);
        }

        // Health tag match (+10%)
        if (profile.health_goal && dish.health_tags?.includes(profile.health_goal)) {
          score += 10;
          reasons.push(`✓ Aligned with health goal (${profile.health_goal})`);
        }

        const finalScore = Math.min(Math.max(score, 10), 99);

        recommended.push({
          dish_id: dish.id,
          name: dish.name,
          price: dish.price,
          cuisine: dish.cuisine,
          match_score: finalScore,
          compatibility_status: 'COMPATIBLE',
          match_reasons: reasons,
        });
      });

      recommended.sort((a, b) => b.match_score - a.match_score);

      setRanking({
        user_id: profile.id,
        recommended_dishes: recommended,
        filtered_dishes: filtered,
      });
    } finally {
      setRankingLoading(false);
    }
  };

  const handleSendFeedback = async (dishId: string, liked: boolean, rating: number) => {
    if (!profile) return;

    setFeedbackState((prev) => ({
      ...prev,
      [dishId]: { ...prev[dishId], loading: true },
    }));

    const payload: FeedbackInput = {
      user_id: profile.id,
      dish_id: dishId,
      liked,
      rating,
    };

    try {
      const res = await apiRequest<FeedbackResult>('/feedback', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setFeedbackState((prev) => ({
        ...prev,
        [dishId]: { liked, rating, status: res.message || 'Feedback saved ✓', loading: false },
      }));
    } catch {
      // Local fallback confirmation
      setFeedbackState((prev) => ({
        ...prev,
        [dishId]: { liked, rating, status: 'Feedback recorded (Local) ✓', loading: false },
      }));
    }
  };

  // Helper map for dish lookup
  const dishMap = new Map(dishes.map((d) => [d.id, d]));

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 max-w-5xl mx-auto space-y-6">
      {/* Header & Personalization Control */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-100 pb-4 gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{restaurantName}</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Total Menu Items: {dishes.length} | Diner: {profile ? profile.name : 'Guest (No Profile Loaded)'}
          </p>
        </div>

        <button
          onClick={handleRunRecommendation}
          disabled={rankingLoading}
          className="px-5 py-2.5 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white text-sm font-semibold rounded-lg shadow-sm transition-colors"
        >
          {rankingLoading ? 'Calculating Personalization...' : '⚡ Personalize Menu'}
        </button>
      </div>

      {rankingError && (
        <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm">
          {rankingError}
        </div>
      )}

      {/* Tabs */}
      <div className="flex flex-wrap border-b border-slate-200 gap-1">
        <button
          onClick={() => setActiveTab('recommended')}
          className={`py-2 px-4 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'recommended'
              ? 'border-orange-600 text-orange-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          ✨ Top Recommended ({ranking?.recommended_dishes.length ?? 0})
        </button>

        <button
          onClick={() => setActiveTab('filtered')}
          className={`py-2 px-4 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'filtered'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          ⚠️ Incompatible / Safety Filtered ({ranking?.filtered_dishes.length ?? 0})
        </button>

        <button
          onClick={() => setActiveTab('all')}
          className={`py-2 px-4 text-sm font-semibold border-b-2 transition-colors ${
            activeTab === 'all'
              ? 'border-slate-800 text-slate-900'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          📖 Full Restaurant Menu ({dishes.length})
        </button>
      </div>

      {/* 1. Recommended Tab */}
      {activeTab === 'recommended' && (
        <div className="space-y-4">
          {!ranking ? (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-500">
              Click <span className="font-semibold text-orange-600">"⚡ Personalize Menu"</span> above to compute rule-based match scores and explanations tailored to your profile.
            </div>
          ) : ranking.recommended_dishes.length === 0 ? (
            <div className="p-6 text-center text-slate-500">No compatible recommendations found matching your parameters.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {ranking.recommended_dishes.map((rec) => {
                const rawDish = dishMap.get(rec.dish_id);
                const feedback = feedbackState[rec.dish_id];

                return (
                  <div
                    key={rec.dish_id}
                    className="p-5 border border-emerald-200 rounded-xl bg-emerald-50/30 hover:shadow-md transition-shadow relative flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">{rec.name}</h3>
                          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 uppercase tracking-wide">
                            {rec.cuisine}
                          </span>
                        </div>

                        <div className="text-right">
                          <div className="text-lg font-extrabold text-orange-600">₹{rec.price}</div>
                          <div className="inline-block px-2.5 py-0.5 text-xs font-bold rounded-full bg-emerald-600 text-white shadow-sm">
                            {rec.match_score}% Match
                          </div>
                        </div>
                      </div>

                      {rawDish?.description && (
                        <p className="text-xs text-slate-600 mb-3 italic">{rawDish.description}</p>
                      )}

                      {/* Reasons */}
                      <div className="mt-3 bg-white p-3 rounded-lg border border-slate-100 space-y-1">
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Why Recommended:</div>
                        {rec.match_reasons.map((reason, rIdx) => (
                          <div key={rIdx} className="text-xs text-slate-700 flex items-center gap-1">
                            <span>{reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Feedback Bar */}
                    <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleSendFeedback(rec.dish_id, true, 5)}
                          disabled={feedback?.loading}
                          className={`px-2.5 py-1 rounded font-medium border ${
                            feedback?.liked === true ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-700 hover:bg-slate-100 border-slate-200'
                          }`}
                        >
                          👍 Like
                        </button>
                        <button
                          onClick={() => handleSendFeedback(rec.dish_id, false, 1)}
                          disabled={feedback?.loading}
                          className={`px-2.5 py-1 rounded font-medium border ${
                            feedback?.liked === false ? 'bg-rose-600 text-white border-rose-600' : 'bg-white text-slate-700 hover:bg-slate-100 border-slate-200'
                          }`}
                        >
                          👎 Dislike
                        </button>
                      </div>

                      {feedback?.status && (
                        <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                          {feedback.status}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* 2. Filtered Tab */}
      {activeTab === 'filtered' && (
        <div className="space-y-4">
          {!ranking ? (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-500">
              Run personalization to view safety filter results.
            </div>
          ) : ranking.filtered_dishes.length === 0 ? (
            <div className="p-6 text-center text-slate-500">No dishes were filtered out by hard constraints.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {ranking.filtered_dishes.map((filt) => (
                <div key={filt.dish_id} className="p-5 border border-rose-200 rounded-xl bg-rose-50/40">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-bold text-slate-800">{filt.name}</h3>
                    <span className="text-sm font-bold text-slate-600">₹{filt.price}</span>
                  </div>

                  <div className="mt-2 p-3 bg-white rounded-lg border border-rose-100 space-y-1">
                    <span className="inline-block px-2 py-0.5 text-xs font-bold rounded bg-rose-600 text-white mb-1">
                      ⚠️ Incompatible / Safety Excluded
                    </span>
                    {filt.exclusion_reasons.map((reason, idx) => (
                      <p key={idx} className="text-xs text-rose-700 font-medium">
                        {reason}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 3. Full Menu Tab */}
      {activeTab === 'all' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dishes.map((dish) => (
            <div key={dish.id} className="p-5 border border-slate-200 rounded-xl bg-white space-y-2">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{dish.name}</h3>
                  <span className="text-xs font-semibold text-slate-500 uppercase">{dish.cuisine} • {dish.diet_type}</span>
                </div>
                <div className="text-lg font-extrabold text-slate-800">₹{dish.price}</div>
              </div>

              {dish.description && <p className="text-xs text-slate-600 italic">{dish.description}</p>}

              {dish.ingredients && dish.ingredients.length > 0 && (
                <div className="text-xs text-slate-500">
                  <strong>Ingredients:</strong> {dish.ingredients.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
