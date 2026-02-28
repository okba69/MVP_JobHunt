"use client";

import { useState, useEffect } from "react";
import { CheckCircle2, ChevronRight, Briefcase, MapPin, Calendar, Building2, MousePointerClick, Search, Loader2 } from "lucide-react";

export function OffersListBuilder() {
    const [offers, setOffers] = useState<any[]>([]);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);

    const [keyword, setKeyword] = useState("");
    const [isScraping, setIsScraping] = useState(false);

    const fetchJobs = () => {
        setLoading(true);
        fetch("http://localhost:8000/api/jobs")
            .then(res => res.json())
            .then(data => {
                setOffers(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching jobs:", err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchJobs();
    }, []);

    const handleScrape = async () => {
        if (!keyword.trim()) return;
        setIsScraping(true);
        try {
            const res = await fetch("http://localhost:8000/api/scrape", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ keyword })
            });
            const data = await res.json();
            if (data.status === "success") {
                fetchJobs(); // Rafraîchir la liste avec les nouvelles offres
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsScraping(false);
        }
    };

    const toggleSelection = (id: number) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(item => item !== id)
                : prev.length < 5 ? [...prev, id] : prev
        );
    };

    const selectAllOffers = () => {
        setSelectedIds(offers.slice(0, 5).map(o => o.id));
    };

    const isSelected = (id: number) => selectedIds.includes(id);
    const isMaxReached = selectedIds.length >= 5;

    return (
        <div className="flex flex-col h-full space-y-8 animate-in fade-in duration-700">

            {/* Header section with sophisticated typography */}
            <div className="flex justify-between items-end border-b border-white/5 pb-6">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-widest mb-4">
                        <MousePointerClick className="w-3.5 h-3.5" /> Sélection Manuelle
                    </div>
                    <h2 className="text-3xl font-semibold text-white tracking-tight">Nouvelles Offres</h2>
                    <p className="text-gray-400 text-sm mt-2 max-w-lg">Sélectionnez jusqu'à 5 offres pertinentes. Notre moteur IA générera un lot de candidatures ultra-personnalisées pour chaque sélection.</p>

                    {/* Real-time Scraping Bar */}
                    <div className="mt-6 flex items-center gap-3">
                        <div className="relative">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                            <input
                                type="text"
                                placeholder="Mot-clé (ex: Data Engineer)"
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                                className="bg-[#0a0a0a] border border-white/10 text-white text-sm rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-blue-500/50 transition-colors w-72 shadow-inner shadow-white/5"
                                onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
                            />
                        </div>
                        <button
                            onClick={handleScrape}
                            disabled={isScraping || !keyword.trim()}
                            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${isScraping ? 'bg-blue-500/50 text-white/50 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-500 hover:shadow-[0_0_15px_rgba(37,99,235,0.4)]'}`}
                        >
                            {isScraping ? (
                                <><Loader2 className="w-4 h-4 animate-spin" /> Scraping...</>
                            ) : (
                                <>Lancer le Scraping</>
                            )}
                        </button>
                    </div>
                </div>

                <div className="flex flex-col items-end gap-3 text-sm">
                    <button
                        onClick={selectAllOffers}
                        className="text-gray-400 hover:text-white transition-colors cursor-pointer flex items-center gap-1.5"
                    >
                        Sélection rapide (Top 5)
                    </button>
                    <div className="flex items-center gap-2 bg-[#0a0a0a] border border-white/5 px-4 py-2 rounded-xl shadow-inner shadow-white/5">
                        <span className={`font-semibold ${selectedIds.length === 5 ? "text-emerald-400" : "text-white"}`}>
                            {selectedIds.length}
                        </span>
                        <span className="text-gray-500">/ 5 sélectionnées</span>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64 text-gray-500">
                    Chargement des offres...
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-32">
                    {offers.map((offer) => (
                        <div
                            key={offer.id}
                            onClick={() => toggleSelection(offer.id)}
                            className={`
              relative group flex flex-col p-6 rounded-2xl border transition-all duration-300 cursor-pointer overflow-hidden
              ${isSelected(offer.id)
                                    ? "border-blue-500/50 bg-[#0a0a0a] shadow-[0_8px_30px_rgba(59,130,246,0.15)] -translate-y-1"
                                    : "border-white/5 bg-[#0a0a0a] hover:border-white/10 hover:bg-[#0f0f0f] hover:-translate-y-0.5 hover:shadow-2xl"}
              ${!isSelected(offer.id) && isMaxReached ? "opacity-40 grayscale-[50%] cursor-not-allowed hover:-translate-y-0" : ""}
            `}
                        >
                            {/* Subtle glass reflection on selected card */}
                            {isSelected(offer.id) && (
                                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none" />
                            )}

                            <div className="flex justify-between items-start mb-4 relative z-10">
                                <div className="flex items-center gap-3">
                                    <div className={`p-0.5 rounded-full bg-[#050505] transition-transform duration-300 ${isSelected(offer.id) ? "scale-110" : "scale-100"}`}>
                                        <CheckCircle2 className={`w-6 h-6 ${isSelected(offer.id) ? "text-blue-500 fill-blue-500/20" : "text-gray-600 group-hover:text-gray-400"} transition-colors`} />
                                    </div>
                                    <h3 className="font-medium text-lg text-white tracking-tight line-clamp-1">{offer.title}</h3>
                                </div>

                                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] uppercase tracking-wider font-semibold bg-white/5 text-gray-400 border border-white/5 whitespace-nowrap">
                                    {offer.source}
                                </span>
                            </div>

                            <div className="flex flex-wrap items-center text-sm text-gray-400 gap-y-3 gap-x-5 mt-auto relative z-10 pl-9">
                                <div className="flex items-center font-medium text-gray-300">
                                    <Building2 className="w-4 h-4 mr-2 text-gray-500" />
                                    {offer.company}
                                </div>
                                <div className="flex items-center">
                                    <MapPin className="w-4 h-4 mr-2 text-gray-500" />
                                    {offer.location}
                                </div>
                                <div className="flex items-center px-2 py-0.5 rounded-md bg-white/5 border border-white/5">
                                    {offer.contract_type}
                                </div>
                                <div className="flex items-center text-xs">
                                    {offer.published_date}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Floating Action Bar - Pro Max Glassmorphism */}
            <div className={`
        fixed bottom-10 left-1/2 transform -translate-x-1/2 ml-36 z-50
        transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]
        ${selectedIds.length > 0 ? "translate-y-0 opacity-100 scale-100" : "translate-y-16 opacity-0 scale-95 pointer-events-none"}
      `}>
                <div className="bg-[#0a0a0a]/80 backdrop-blur-2xl border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)] rounded-2xl p-2.5 flex items-center gap-4">
                    <div className="px-5 py-2 flex flex-col items-center border-r border-white/10">
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                            {selectedIds.length}
                        </span>
                        <span className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold mt-0.5">Offres</span>
                    </div>

                    <div className="text-sm pr-4">
                        <p className="text-gray-200 font-medium tracking-tight">Prêt pour la génération</p>
                        <p className="text-gray-500 text-xs">Les canevas CV et LM seront fusionnés.</p>
                    </div>

                    <button
                        className={`
              flex items-center gap-2 px-6 py-3.5 rounded-xl font-medium transition-all duration-300 cursor-pointer shadow-lg
              ${selectedIds.length > 0
                                ? "bg-white text-black hover:bg-gray-200 hover:scale-[1.02] shadow-[0_0_20px_rgba(255,255,255,0.2)]"
                                : "bg-gray-800 text-gray-500 cursor-not-allowed"}
            `}
                        disabled={selectedIds.length === 0}
                    >
                        <span>Générer le lot</span>
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
