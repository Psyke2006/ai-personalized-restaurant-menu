'use client';

import React, { useState } from 'react';
import { DishInput, ManualMenuInput, ManualMenuResult, MenuUploadResult, UnifiedDish } from '@/types/api';
import { apiRequest, ApiRequestError } from '@/lib/api-client';

interface MenuIngestionProps {
  onMenuLoaded: (menuId: string, dishes: UnifiedDish[], restaurantName: string) => void;
}

const SAMPLE_MENU_DISHES: DishInput[] = [
  {
    name: 'Paneer Tikka',
    description: 'Char-grilled cottage cheese marinated in aromatic yogurt and tandoori spices',
    price: 280,
    cuisine: 'Indian',
    ingredients: ['paneer', 'yogurt', 'bell pepper', 'spices'],
    diet_type: 'vegetarian',
    spice_level: 3,
    health_tags: ['high_protein'],
  },
  {
    name: 'Peanut Satay Skewers',
    description: 'Grilled tofu skewers with rich peanut coconut sauce',
    price: 320,
    cuisine: 'Thai',
    ingredients: ['tofu', 'peanuts', 'coconut milk', 'chili'],
    diet_type: 'vegan',
    spice_level: 4,
    health_tags: ['high_protein'],
  },
  {
    name: 'Margherita Pizza',
    description: 'Classic sourdough pizza topped with fresh mozzarella, basil, and tomato sauce',
    price: 450,
    cuisine: 'Italian',
    ingredients: ['flour', 'mozzarella', 'tomato', 'basil'],
    diet_type: 'vegetarian',
    spice_level: 1,
    health_tags: ['comfort_food'],
  },
  {
    name: 'Chicken Biryani',
    description: 'Fragrant basmati rice cooked with marinated chicken and saffron',
    price: 380,
    cuisine: 'Indian',
    ingredients: ['chicken', 'basmati rice', 'spices', 'ghee'],
    diet_type: 'non-vegetarian',
    spice_level: 3,
    health_tags: ['high_protein'],
  },
  {
    name: 'Mushroom Risotto',
    description: 'Creamy arborio rice infused with wild mushrooms and parmesan',
    price: 420,
    cuisine: 'Italian',
    ingredients: ['arborio rice', 'wild mushroom', 'parmesan', 'butter'],
    diet_type: 'vegetarian',
    spice_level: 1,
    health_tags: ['low_calorie'],
  }
];

export function MenuIngestion({ onMenuLoaded }: MenuIngestionProps) {
  const [activeTab, setActiveTab] = useState<'sample' | 'manual' | 'upload'>('sample');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Upload Tab state
  const [file, setFile] = useState<File | null>(null);
  const [uploadRestaurant, setUploadRestaurant] = useState('Gourmet Bistro');

  // Manual Tab state
  const [manualRestaurant, setManualRestaurant] = useState('Custom Restaurant');
  const [dishes, setDishes] = useState<DishInput[]>([
    {
      name: '',
      description: '',
      price: 250,
      cuisine: 'Indian',
      ingredients: [],
      diet_type: 'vegetarian',
      spice_level: 2,
      health_tags: [],
    },
  ]);
  const [ingredientsInput, setIngredientsInput] = useState<string[]>(['']);

  const handleAddDishRow = () => {
    setDishes((prev) => [
      ...prev,
      {
        name: '',
        description: '',
        price: 200,
        cuisine: 'Indian',
        ingredients: [],
        diet_type: 'vegetarian',
        spice_level: 2,
        health_tags: [],
      },
    ]);
    setIngredientsInput((prev) => [...prev, '']);
  };

  const handleLoadSampleMenu = async () => {
    setLoading(true);
    setErrorMsg(null);

    const samplePayload: ManualMenuInput = {
      restaurant_name: 'Spice & Taste Bistro',
      dishes: SAMPLE_MENU_DISHES,
    };

    try {
      const result = await apiRequest<ManualMenuResult>('/menu/manual', {
        method: 'POST',
        body: JSON.stringify(samplePayload),
      });

      const unifiedDishes: UnifiedDish[] = SAMPLE_MENU_DISHES.map((d, index) => ({
        ...d,
        id: `d-sample-${index + 1}`,
      }));

      onMenuLoaded(result.menu_id, unifiedDishes, result.restaurant_name);
    } catch {
      // Fallback for local demo if backend is offline
      const mockMenuId = `m-sample-${Date.now()}`;
      const unifiedDishes: UnifiedDish[] = SAMPLE_MENU_DISHES.map((d, index) => ({
        ...d,
        id: `d-sample-${index + 1}`,
      }));
      onMenuLoaded(mockMenuId, unifiedDishes, 'Spice & Taste Bistro (Local Demo Menu)');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMsg('Please select a PDF or Image file to upload.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', file);
    if (uploadRestaurant.trim()) {
      formData.append('restaurant_name', uploadRestaurant.trim());
    }

    try {
      const result = await apiRequest<MenuUploadResult>('/menu/upload', {
        method: 'POST',
        body: formData,
      });

      const unifiedDishes: UnifiedDish[] = result.dishes.map((d) => ({
        id: d.id,
        name: d.name,
        price: d.price,
        cuisine: d.cuisine,
        ingredients: d.ingredients,
        diet_type: d.diet_type,
        spice_level: d.spice_level,
        health_tags: d.health_tags,
      }));

      onMenuLoaded(result.menu_id, unifiedDishes, uploadRestaurant || 'Uploaded Restaurant Menu');
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Failed to process menu upload. Please check backend connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    const formattedDishes: DishInput[] = dishes.map((d, i) => ({
      ...d,
      ingredients: (ingredientsInput[i] || '')
        .split(',')
        .map((s) => s.trim().toLowerCase())
        .filter((s) => s.length > 0),
    }));

    const payload: ManualMenuInput = {
      restaurant_name: manualRestaurant.trim() || 'Manual Entry Menu',
      dishes: formattedDishes,
    };

    try {
      const result = await apiRequest<ManualMenuResult>('/menu/manual', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const unifiedDishes: UnifiedDish[] = formattedDishes.map((d, index) => ({
        ...d,
        id: `d-manual-${index + 1}`,
      }));

      onMenuLoaded(result.menu_id, unifiedDishes, result.restaurant_name);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setErrorMsg(err.message);
      } else {
        // Local fallback
        const mockMenuId = `m-manual-${Date.now()}`;
        const unifiedDishes: UnifiedDish[] = formattedDishes.map((d, index) => ({
          ...d,
          id: `d-manual-${index + 1}`,
        }));
        onMenuLoaded(mockMenuId, unifiedDishes, manualRestaurant);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 max-w-3xl mx-auto">
      <div className="border-b border-slate-100 pb-4 mb-6">
        <h2 className="text-xl font-bold text-slate-800">2. Restaurant Menu Ingestion</h2>
        <p className="text-sm text-slate-500 mt-1">
          Provide a restaurant menu using one of the ingestion channels below.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 mb-6">
        <button
          onClick={() => setActiveTab('sample')}
          className={`py-2 px-4 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'sample'
              ? 'border-orange-600 text-orange-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          Curated Sample Menu (Instant)
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`py-2 px-4 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'upload'
              ? 'border-orange-600 text-orange-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          Upload File (PDF / Image OCR)
        </button>
        <button
          onClick={() => setActiveTab('manual')}
          className={`py-2 px-4 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'manual'
              ? 'border-orange-600 text-orange-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          Manual Dish Entry
        </button>
      </div>

      {errorMsg && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {errorMsg}
        </div>
      )}

      {/* Sample Menu Tab */}
      {activeTab === 'sample' && (
        <div className="space-y-4 text-slate-700">
          <p className="text-sm text-slate-600">
            Load a pre-configured multi-cuisine restaurant menu with diverse dietary attributes (Paneer Tikka, Peanut Satay, Biryani, Margherita Pizza, Risotto) for instant recommendation testing.
          </p>
          <button
            onClick={handleLoadSampleMenu}
            disabled={loading}
            className="px-6 py-2.5 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white font-medium text-sm rounded-lg shadow-sm transition-colors"
          >
            {loading ? 'Ingesting Sample Menu...' : 'Load Curated Sample Menu'}
          </button>
        </div>
      )}

      {/* File Upload Tab */}
      {activeTab === 'upload' && (
        <form onSubmit={handleFileUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Restaurant Name</label>
            <input
              type="text"
              value={uploadRestaurant}
              onChange={(e) => setUploadRestaurant(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Select Menu File (PDF or Image)</label>
            <input
              type="file"
              accept=".pdf,image/png,image/jpeg,image/jpg,image/webp"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white font-medium text-sm rounded-lg shadow-sm transition-colors"
          >
            {loading ? 'Extracting via PyMuPDF/OCR/Gemini...' : 'Upload & Process Menu'}
          </button>
        </form>
      )}

      {/* Manual Entry Tab */}
      {activeTab === 'manual' && (
        <form onSubmit={handleManualSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Restaurant Name</label>
            <input
              type="text"
              value={manualRestaurant}
              onChange={(e) => setManualRestaurant(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-orange-500"
            />
          </div>

          {dishes.map((dish, idx) => (
            <div key={idx} className="p-4 border border-slate-200 rounded-lg space-y-3 bg-slate-50">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Dish #{idx + 1}</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Dish Name"
                  value={dish.name}
                  onChange={(e) => {
                    const newDishes = [...dishes];
                    newDishes[idx].name = e.target.value;
                    setDishes(newDishes);
                  }}
                  required
                  className="px-3 py-1.5 border border-slate-300 rounded text-sm bg-white"
                />
                <input
                  type="number"
                  placeholder="Price (₹)"
                  value={dish.price}
                  onChange={(e) => {
                    const newDishes = [...dishes];
                    newDishes[idx].price = parseFloat(e.target.value) || 0;
                    setDishes(newDishes);
                  }}
                  required
                  className="px-3 py-1.5 border border-slate-300 rounded text-sm bg-white"
                />
                <input
                  type="text"
                  placeholder="Cuisine (e.g. Indian)"
                  value={dish.cuisine}
                  onChange={(e) => {
                    const newDishes = [...dishes];
                    newDishes[idx].cuisine = e.target.value;
                    setDishes(newDishes);
                  }}
                  className="px-3 py-1.5 border border-slate-300 rounded text-sm bg-white"
                />
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Ingredients (comma separated)"
                  value={ingredientsInput[idx] || ''}
                  onChange={(e) => {
                    const newInputs = [...ingredientsInput];
                    newInputs[idx] = e.target.value;
                    setIngredientsInput(newInputs);
                  }}
                  className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm bg-white"
                />
              </div>
            </div>
          ))}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleAddDishRow}
              className="px-4 py-2 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-sm"
            >
              + Add Another Dish
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-medium"
            >
              {loading ? 'Submitting Menu...' : 'Submit Manual Menu'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
