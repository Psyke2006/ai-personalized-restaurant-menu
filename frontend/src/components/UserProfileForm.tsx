'use client';

import React, { useState } from 'react';
import { UserProfile, UserProfileInput } from '@/types/api';
import { apiRequest, ApiRequestError } from '@/lib/api-client';

interface UserProfileFormProps {
  onProfileSaved: (profile: UserProfile) => void;
  initialProfile?: UserProfile | null;
}

const COMMON_DIETS = [
  { id: 'vegetarian', label: 'Vegetarian' },
  { id: 'vegan', label: 'Vegan' },
  { id: 'jain', label: 'Jain' },
  { id: 'halal', label: 'Halal' },
  { id: 'non-vegetarian', label: 'Non-Vegetarian' },
  { id: 'gluten-free', label: 'Gluten-Free' },
];

export function UserProfileForm({ onProfileSaved, initialProfile }: UserProfileFormProps) {
  const [formData, setFormData] = useState<UserProfileInput>({
    name: initialProfile?.name ?? '',
    budget: initialProfile?.budget ?? 500,
    spice_tolerance: initialProfile?.spice_tolerance ?? 3,
    health_goal: initialProfile?.health_goal ?? 'high_protein',
    dietary_preferences: initialProfile?.dietary_preferences ?? ['vegetarian'],
    allergies: initialProfile?.allergies ?? [],
    favorite_cuisines: initialProfile?.favorite_cuisines ?? ['Indian'],
    favorite_ingredients: initialProfile?.favorite_ingredients ?? ['paneer'],
  });

  const [allergiesText, setAllergiesText] = useState(initialProfile?.allergies?.join(', ') ?? '');
  const [cuisinesText, setCuisinesText] = useState(initialProfile?.favorite_cuisines?.join(', ') ?? 'Indian, Italian');
  const [ingredientsText, setIngredientsText] = useState(initialProfile?.favorite_ingredients?.join(', ') ?? 'paneer, mushroom');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    if (isNaN(formData.budget) || formData.budget < 0) {
      errors.budget = 'Budget must be a non-negative number';
    }
    if (formData.spice_tolerance < 1 || formData.spice_tolerance > 5) {
      errors.spice_tolerance = 'Spice tolerance must be between 1 and 5';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleDietToggle = (dietId: string) => {
    setFormData((prev) => {
      const exists = prev.dietary_preferences.includes(dietId);
      const updated = exists
        ? prev.dietary_preferences.filter((d) => d !== dietId)
        : [...prev.dietary_preferences, dietId];
      return { ...prev, dietary_preferences: updated };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!validate()) return;

    setLoading(true);

    const parseTags = (str: string) =>
      str
        .split(',')
        .map((s) => s.trim().toLowerCase())
        .filter((s) => s.length > 0);

    const payload: UserProfileInput = {
      ...formData,
      name: formData.name.trim() || 'Guest Diner',
      allergies: parseTags(allergiesText),
      favorite_cuisines: parseTags(cuisinesText),
      favorite_ingredients: parseTags(ingredientsText),
    };

    try {
      const savedProfile = await apiRequest<UserProfile>('/users/profile', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setSuccessMsg(`Profile saved successfully! User ID: ${savedProfile.id}`);
      onProfileSaved(savedProfile);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setErrorMsg(err.message);
      } else {
        // Fallback offline mock profile generation for local UI verification
        const mockProfile: UserProfile = {
          ...payload,
          id: `u-local-${Date.now()}`,
          created_at: new Date().toISOString(),
        };
        setErrorMsg('Could not reach FastAPI backend server. Profile saved in local state for testing.');
        onProfileSaved(mockProfile);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 max-w-3xl mx-auto">
      <div className="border-b border-slate-100 pb-4 mb-6">
        <h2 className="text-xl font-bold text-slate-800">1. Diner Preference Profile</h2>
        <p className="text-sm text-slate-500 mt-1">
          Set your dietary constraints, allergies, and taste preferences to personalize your menu experience.
        </p>
      </div>

      {errorMsg && (
        <div className="mb-6 p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm">
          <strong>Notice:</strong> {errorMsg}
        </div>
      )}

      {successMsg && (
        <div className="mb-6 p-4 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm">
          {successMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name & Budget */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Diner Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Tanishkk"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Budget (₹ INR)</label>
            <input
              type="number"
              min="0"
              step="50"
              value={formData.budget}
              onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            />
            {fieldErrors.budget && <p className="text-xs text-red-600 mt-1">{fieldErrors.budget}</p>}
          </div>
        </div>

        {/* Spice Level & Health Goal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Spice Tolerance: Level {formData.spice_tolerance}
            </label>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={formData.spice_tolerance}
              onChange={(e) => setFormData({ ...formData, spice_tolerance: parseInt(e.target.value) })}
              className="w-full accent-orange-600"
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>1 (Mild)</span>
              <span>3 (Medium)</span>
              <span>5 (Spicy 🔥)</span>
            </div>
            {fieldErrors.spice_tolerance && <p className="text-xs text-red-600 mt-1">{fieldErrors.spice_tolerance}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Health Goal</label>
            <select
              value={formData.health_goal}
              onChange={(e) => setFormData({ ...formData, health_goal: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            >
              <option value="high_protein">High Protein</option>
              <option value="low_carb">Low Carb</option>
              <option value="low_calorie">Low Calorie / Balanced</option>
              <option value="heart_healthy">Heart Healthy</option>
              <option value="none">General / No Specific Goal</option>
            </select>
          </div>
        </div>

        {/* Dietary Preferences */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Dietary Restrictions</label>
          <div className="flex flex-wrap gap-2">
            {COMMON_DIETS.map((diet) => {
              const selected = formData.dietary_preferences.includes(diet.id);
              return (
                <button
                  key={diet.id}
                  type="button"
                  onClick={() => handleDietToggle(diet.id)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    selected
                      ? 'bg-orange-600 text-white border-orange-600'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {diet.label} {selected && '✓'}
                </button>
              );
            })}
          </div>
        </div>

        {/* Allergies */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Food Allergies <span className="text-red-500 font-bold">*Strict Safety Filter</span>
          </label>
          <input
            type="text"
            value={allergiesText}
            onChange={(e) => setAllergiesText(e.target.value)}
            placeholder="e.g. peanuts, shellfish, tree nuts (comma separated)"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
          />
          <p className="text-xs text-slate-500 mt-1">
            Dishes matching these allergens will be strictly excluded from recommendations with clear safety warnings.
          </p>
        </div>

        {/* Favorite Cuisines & Ingredients */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Favorite Cuisines</label>
            <input
              type="text"
              value={cuisinesText}
              onChange={(e) => setCuisinesText(e.target.value)}
              placeholder="e.g., Indian, Italian, Thai"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Favorite Ingredients</label>
            <input
              type="text"
              value={ingredientsText}
              onChange={(e) => setIngredientsText(e.target.value)}
              placeholder="e.g., paneer, mushroom, garlic"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
            />
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto px-6 py-2.5 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white font-medium text-sm rounded-lg shadow-sm transition-colors"
          >
            {loading ? 'Saving Profile...' : 'Save & Update Preferences'}
          </button>
        </div>
      </form>
    </div>
  );
}
