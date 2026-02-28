"use client";

import { useState } from "react";
import { CheckCircle2, ChevronRight, Briefcase, MapPin, Calendar, Building2, CheckSquare, Square } from "lucide-react";

// Mock data based on our scrapers
const mockOffers = [
    { id: 1, title: "INGENIEUR EXLOITATION", company: "Engie", location: "Etrez, France", contract: "CDD", date: "28/02/2026", source: "engie-jobs" },
    { id: 2, title: "Ingénieur d'Exploitation H/F", company: "Engie", location: "Echirolles, France", contract: "CDI", date: "28/02/2026", source: "engie-jobs" },
    { id: 3, title: "Ingénieur Data Pipeline", company: "TotalEnergies", location: "Paris, France", contract: "CDI", date: "27/02/2026", source: "totalenergies" },
    { id: 4, title: "Ingénieur Système Aéronautique", company: "Airbus", location: "Toulouse, France", contract: "CDI", date: "26/02/2026", source: "airbus" },
    { id: 5, title: "Ingénieur Méthodes Industrielles", company: "Safran", location: "Bordeaux, France", contract: "CDI", date: "25/02/2026", source: "safran" },
    { id: 6, title: "Chef de Projet Déploiement", company: "EDF", location: "Lyon, France", contract: "CDI", date: "24/02/2026", source: "edf" },
];

export function OffersListBuilder() {
    const [selectedIds, setSelectedIds] = useState<number[]>([]);

    const toggleSelection = (id: number) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(item => item !== id)
                : prev.length < 5 ? [...prev, id] : prev
        );
    };

    const selectAllMocks = () => {
        setSelectedIds(mockOffers.slice(0, 5).map(o => o.id));
    };

    const isSelected = (id: number) => selectedIds.includes(id);
    const isMaxReached = selectedIds.length >= 5;

    return (
        <div className="flex flex-col h-full space-y-6">
            <div className="flex justify-between items-end border-b border-gray-800 pb-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-50 tracking-tight">Nouvelles Offres Scrappées</h2>
                    <p className="text-gray-400 text-sm mt-1">Sélectionnez jusqu'à 5 offres pour générer vos candidatures sur mesure.</p>
                </div>
                <div className="flex items-center space-x-4">
                    <div className="text-sm font-medium bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-full">
                        <span className={selectedIds.length === 5 ? "text-green-400 font-bold" : "text-blue-400"}>{selectedIds.length}</span> / 5 sélectionnées
                    </div>
                    <button
                        onClick={selectAllMocks}
                        className="text-sm text-gray-400 hover:text-gray-200 transition-colors cursor-pointer"
                    >
                        Sélection rapide (Top 5)
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-3 overflow-y-auto pr-2 pb-24">
                {mockOffers.map((offer) => (
                    <div
                        key={offer.id}
                        onClick={() => toggleSelection(offer.id)}
                        className={`
              relative group flex items-center p-4 rounded-xl border transition-all duration-200 cursor-pointer
              ${isSelected(offer.id)
                                ? "border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.15)]"
                                : "border-gray-800 bg-gray-900/50 hover:bg-gray-800 hover:border-gray-700"}
              ${!isSelected(offer.id) && isMaxReached ? "opacity-50 cursor-not-allowed" : ""}
            `}
                    >
                        {/* Checkbox indicator */}
                        <div className="mr-4 flex-shrink-0">
                            {isSelected(offer.id) ? (
                                <CheckSquare className="w-6 h-6 text-blue-500 drop-shadow-sm" />
                            ) : (
                                <Square className="w-6 h-6 text-gray-600 group-hover:text-gray-400 transition-colors" />
                            )}
                        </div>

                        {/* Content */}
                        <div className="flex-grow min-w-0">
                            <div className="flex justify-between items-start mb-1">
                                <h3 className={`font-semibold text-lg truncate pr-4 ${isSelected(offer.id) ? "text-blue-50" : "text-gray-100"}`}>
                                    {offer.title}
                                </h3>
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-800 text-gray-300 whitespace-nowrap">
                                    {offer.source}
                                </span>
                            </div>

                            <div className="flex flex-wrap items-center text-sm text-gray-400 gap-y-2 gap-x-4">
                                <div className="flex items-center">
                                    <Building2 className="w-4 h-4 mr-1.5 text-gray-500" />
                                    <span className={isSelected(offer.id) ? "text-blue-200 font-medium" : ""}>{offer.company}</span>
                                </div>
                                <div className="flex items-center">
                                    <MapPin className="w-4 h-4 mr-1.5 text-gray-500" />
                                    {offer.location}
                                </div>
                                <div className="flex items-center">
                                    <Briefcase className="w-4 h-4 mr-1.5 text-gray-500" />
                                    {offer.contract}
                                </div>
                                <div className="flex items-center">
                                    <Calendar className="w-4 h-4 mr-1.5 text-gray-500" />
                                    {offer.date}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Floating Action Bar */}
            <div className={`
        fixed bottom-8 left-1/2 transform -translate-x-1/2 ml-32
        transition-all duration-300 ease-out
        ${selectedIds.length > 0 ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0 pointer-events-none"}
      `}>
                <div className="bg-gray-900 border border-gray-800 shadow-2xl rounded-2xl p-4 flex items-center space-x-6 backdrop-blur-xl bg-opacity-90">
                    <div className="flex items-center space-x-3">
                        <div className="bg-blue-500/20 text-blue-400 w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg border border-blue-500/30">
                            {selectedIds.length}
                        </div>
                        <div className="text-sm">
                            <p className="text-gray-200 font-medium">Offres sélectionnées</p>
                            <p className="text-gray-500">Prêt pour la génération</p>
                        </div>
                    </div>

                    <button
                        className={`
              flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 cursor-pointer shadow-lg
              ${selectedIds.length > 0
                                ? "bg-blue-600 hover:bg-blue-500 text-white hover:shadow-[0_0_20px_rgba(37,99,235,0.4)]"
                                : "bg-gray-800 text-gray-500 cursor-not-allowed"}
            `}
                        disabled={selectedIds.length === 0}
                    >
                        <span>Générer les Candidatures</span>
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
