'use client';

import React, { useState } from 'react';
import { UserProfileForm } from '@/components/UserProfileForm';
import { MenuIngestion } from '@/components/MenuIngestion';
import { MenuDisplay } from '@/components/MenuDisplay';
import { UnifiedDish, UserProfile } from '@/types/api';

export default function Home() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [menuId, setMenuId] = useState<string | null>(null);
  const [restaurantName, setRestaurantName] = useState<string>('');
  const [dishes, setDishes] = useState<UnifiedDish[]>([]);

  const handleProfileSaved = (savedProfile: UserProfile) => {
    setProfile(savedProfile);
  };

  const handleMenuLoaded = (loadedMenuId: string, loadedDishes: UnifiedDish[], name: string) => {
    setMenuId(loadedMenuId);
    setDishes(loadedDishes);
    setRestaurantName(name);
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 pb-16">
      {/* Navbar Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🍽️</span>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900 leading-tight">
                AI Personalized Menu
              </h1>
              <p className="text-xs text-slate-500 font-medium">
                PBL Prototype • Constraint-Aware & Explainable Recommendation
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {profile && (
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-orange-100 text-orange-800">
                👤 {profile.name} (₹{profile.budget})
              </span>
            )}
            {menuId && (
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800">
                📖 {restaurantName} ({dishes.length} Items)
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Body */}
      <div className="max-w-6xl mx-auto px-4 pt-8 space-y-8">
        {/* Step 1: User Profile Form */}
        <section>
          <UserProfileForm onProfileSaved={handleProfileSaved} initialProfile={profile} />
        </section>

        {/* Step 2: Menu Ingestion */}
        <section>
          <MenuIngestion onMenuLoaded={handleMenuLoaded} />
        </section>

        {/* Step 3: Menu Display & Personalization */}
        {menuId && (
          <section id="personalized-menu">
            <MenuDisplay
              restaurantName={restaurantName}
              menuId={menuId}
              dishes={dishes}
              profile={profile}
            />
          </section>
        )}
      </div>
    </main>
  );
}
