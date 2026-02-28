"use client";

import { useState, useEffect } from "react";
import { CheckCircle2, ChevronRight, Briefcase, MapPin, Calendar, Building2, MousePointerClick, Search, Loader2, RefreshCcw, Filter, ExternalLink } from "lucide-react";

export function OffersListBuilder({ onGenerate }: { onGenerate?: (offers: any[]) => void }) {
    const [offers, setOffers] = useState<any[]>([]);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);

    const [keyword, setKeyword] = useState("");
    const [location, setLocation] = useState("");
    const [contractType, setContractType] = useState("");

    // Scraping state (séparé des filtres locaux)
    const [scrapeKeyword, setScrapeKeyword] = useState("");
    const [isScraping, setIsScraping] = useState(false);
    const [searchResultCount, setSearchResultCount] = useState<number | null>(null);

    const fetchJobs = () => {
        setLoading(true);

        const params = new URLSearchParams();
        if (keyword) params.append("keyword", keyword);
        if (location) params.append("location", location);
        if (contractType) params.append("contract_type", contractType);

        const url = `http://localhost:8000/api/jobs?${params.toString()}`;

        fetch(url)
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

    // Charger les offres au démarrage
    useEffect(() => {
        fetchJobs();
    }, []);

    // Filtrage local instantané quand les filtres changent
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchJobs();
        }, 300); // Debounce 300ms
        return () => clearTimeout(timer);
    }, [keyword, location, contractType]);

    // Le scraping est une action SÉPARÉE : va chercher de NOUVELLES offres sur le web
    const [scrapeMessage, setScrapeMessage] = useState<string | null>(null);
    const [scrapeStatus, setScrapeStatus] = useState<"success" | "cached" | null>(null);

    const handleScrape = async () => {
        if (!scrapeKeyword.trim()) return;
        setIsScraping(true);
        setSearchResultCount(null);
        setScrapeMessage(null);
        setScrapeStatus(null);
        try {
            const res = await fetch("http://localhost:8000/api/scrape", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ keyword: scrapeKeyword })
            });
            const data = await res.json();

            if (data.status === "cached") {
                // Le mot-clé a été scrapé récemment — pas besoin de re-scraper
                setScrapeStatus("cached");
                setScrapeMessage(data.message);
                setSearchResultCount(data.total_in_db || 0);
            } else if (data.status === "success") {
                setScrapeStatus("success");
                setSearchResultCount(data.new_offers_count);
                const sources = data.sources?.join(", ") || "";
                setScrapeMessage(sources ? `Sources: ${sources}` : null);
            }
            // Mettre le mot-clé dans le filtre local pour voir les résultats
            setKeyword(scrapeKeyword);
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

                    {/* Section 1 : Scraping — Aller chercher de NOUVELLES offres */}
                    <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-blue-500/5 to-indigo-500/5 border border-blue-500/10">
                        <div className="flex items-center gap-2 mb-3">
                            <RefreshCcw className="w-3.5 h-3.5 text-blue-400" />
                            <span className="text-xs font-semibold text-blue-300 uppercase tracking-wider">Actualiser depuis le web</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="relative flex-1">
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Mot-clé à scraper (ex: Data Engineer)"
                                    value={scrapeKeyword}
                                    onChange={(e) => setScrapeKeyword(e.target.value)}
                                    className="w-full bg-[#050505] border border-white/10 text-white text-sm rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-blue-500/50 transition-colors"
                                    onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
                                />
                            </div>
                            <button
                                onClick={handleScrape}
                                disabled={isScraping || !scrapeKeyword.trim()}
                                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${isScraping ? 'bg-blue-500/30 text-white/50 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-500 hover:shadow-[0_0_15px_rgba(37,99,235,0.4)] cursor-pointer'}`}
                            >
                                {isScraping ? (
                                    <><Loader2 className="w-4 h-4 animate-spin" /> Scraping...</>
                                ) : (
                                    <><RefreshCcw className="w-4 h-4" /> Actualiser</>
                                )}
                            </button>
                        </div>
                        {scrapeStatus && !isScraping && (
                            <div className={`mt-3 text-sm flex flex-col gap-1 animate-in fade-in ${scrapeStatus === "cached" ? "text-amber-400" : "text-emerald-400"}`}>
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4" />
                                    {scrapeStatus === "cached" ? (
                                        <span>⚡ {scrapeMessage}</span>
                                    ) : (
                                        <span><strong>{searchResultCount}</strong> nouvelle(s) offre(s) ajoutée(s) à la base.</span>
                                    )}
                                </div>
                                {scrapeMessage && scrapeStatus === "success" && (
                                    <span className="text-xs text-gray-500 ml-6">{scrapeMessage}</span>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Section 2 : Filtres locaux — Recherche instantanée dans la base */}
                    <div className="mt-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Filter className="w-3.5 h-3.5 text-gray-400" />
                            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Filtrer les offres existantes</span>
                            <span className="text-xs text-gray-500">({offers.length} résultats)</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-3">
                            <div className="relative flex-1 min-w-[200px] max-w-xs">
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Filtrer par titre, entreprise..."
                                    value={keyword}
                                    onChange={(e) => setKeyword(e.target.value)}
                                    className="w-full bg-[#0a0a0a] border border-white/10 text-white text-sm rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-blue-500/50 transition-colors shadow-inner shadow-white/5"
                                />
                            </div>
                            <div className="relative flex-1 min-w-[180px] max-w-xs">
                                <MapPin className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Ville, Pays (ex: Lyon)"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    className="w-full bg-[#0a0a0a] border border-white/10 text-white text-sm rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-blue-500/50 transition-colors shadow-inner shadow-white/5"
                                />
                            </div>
                            <div className="relative min-w-[150px]">
                                <Briefcase className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                <select
                                    value={contractType}
                                    onChange={(e) => setContractType(e.target.value)}
                                    className="w-full bg-[#0a0a0a] border border-white/10 text-white text-sm rounded-xl pl-10 pr-10 py-2.5 focus:outline-none focus:border-blue-500/50 transition-colors appearance-none shadow-inner shadow-white/5 cursor-pointer"
                                >
                                    <option value="">Tous contrats</option>
                                    <option value="CDI">CDI</option>
                                    <option value="CDD">CDD</option>
                                    <option value="Alternance">Alternance</option>
                                    <option value="Stage">Stage</option>
                                    <option value="Freelance">Freelance</option>
                                </select>
                            </div>
                        </div>
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
                                {offer.url && (
                                    <a
                                        href={offer.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={(e) => e.stopPropagation()}
                                        className="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors ml-auto"
                                        title="Voir l'offre originale"
                                    >
                                        <ExternalLink className="w-3.5 h-3.5" />
                                        <span className="text-xs">Voir</span>
                                    </a>
                                )}
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
                        onClick={() => {
                            if (onGenerate) {
                                const selected = offers.filter(o => selectedIds.includes(o.id));
                                onGenerate(selected);
                            }
                        }}
                    >
                        <span>Générer le lot</span>
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
