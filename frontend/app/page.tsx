"use client";

import { useState } from "react";
import { OffersListBuilder } from "@/components/OffersListBuilder";
import { CanvasEditor } from "@/components/CanvasEditor";

interface JobOffer {
  id: number;
  title: string;
  company: string;
  location: string;
  url: string;
  contract_type: string;
  published_date: string;
  source: string;
}

export default function Home() {
  const [view, setView] = useState<"list" | "canvas">("list");
  const [selectedOffers, setSelectedOffers] = useState<JobOffer[]>([]);

  const handleGenerate = (offers: JobOffer[]) => {
    setSelectedOffers(offers);
    setView("canvas");
  };

  return (
    <div className="h-full">
      {view === "list" ? (
        <OffersListBuilder onGenerate={handleGenerate} />
      ) : (
        <CanvasEditor
          selectedOffers={selectedOffers}
          onBack={() => setView("list")}
        />
      )}
    </div>
  );
}
