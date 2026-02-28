"use client";

import { useState, useEffect } from "react";
import {
    ArrowLeft,
    Building2,
    MapPin,
    Briefcase,
    Calendar,
    ExternalLink,
    FileText,
    Mail,
    Bold,
    Italic,
    Underline,
    AlignLeft,
    AlignCenter,
    AlignRight,
    List,
    Download,
    Sparkles,
    Loader2,
} from "lucide-react";

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

interface CanvasEditorProps {
    selectedOffers: JobOffer[];
    onBack: () => void;
}

export function CanvasEditor({ selectedOffers, onBack }: CanvasEditorProps) {
    const [activeOfferIndex, setActiveOfferIndex] = useState(0);
    const [activeTab, setActiveTab] = useState<"cv" | "lm">("lm");
    const [cvContent, setCvContent] = useState<{ [key: number]: string }>({});
    const [lmContent, setLmContent] = useState<{ [key: number]: string }>({});
    const [isGenerating, setIsGenerating] = useState(false);

    const activeOffer = selectedOffers[activeOfferIndex];

    // Générer un contenu de base pour chaque offre sélectionnée
    useEffect(() => {
        const newCv: { [key: number]: string } = {};
        const newLm: { [key: number]: string } = {};

        selectedOffers.forEach((offer) => {
            newCv[offer.id] = generateCvTemplate(offer);
            newLm[offer.id] = generateLmTemplate(offer);
        });

        setCvContent(newCv);
        setLmContent(newLm);
    }, [selectedOffers]);

    const currentContent =
        activeTab === "cv"
            ? cvContent[activeOffer?.id] || ""
            : lmContent[activeOffer?.id] || "";

    const setCurrentContent = (value: string) => {
        if (activeTab === "cv") {
            setCvContent((prev) => ({ ...prev, [activeOffer.id]: value }));
        } else {
            setLmContent((prev) => ({ ...prev, [activeOffer.id]: value }));
        }
    };

    return (
        <div className="flex flex-col h-full animate-in fade-in duration-500">
            {/* Top bar */}
            <div className="flex items-center justify-between border-b border-white/5 pb-4 mb-6">
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors cursor-pointer group"
                >
                    <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
                    <span className="text-sm">Retour aux offres</span>
                </button>

                <div className="flex items-center gap-3">
                    {/* Offer selector pills */}
                    {selectedOffers.map((offer, index) => (
                        <button
                            key={offer.id}
                            onClick={() => setActiveOfferIndex(index)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${index === activeOfferIndex
                                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                                    : "bg-white/5 text-gray-400 border border-white/5 hover:bg-white/10 hover:text-gray-300"
                                }`}
                        >
                            {offer.company}
                        </button>
                    ))}
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">
                        {activeOfferIndex + 1} / {selectedOffers.length} offres
                    </span>
                </div>
            </div>

            {/* Split screen */}
            <div className="flex flex-1 gap-6 min-h-0">
                {/* LEFT PANEL — Job Offer Details */}
                <div className="w-[38%] flex flex-col gap-4 overflow-y-auto pr-2 scrollbar-thin">
                    {/* Offer Card */}
                    <div className="bg-[#0a0a0a] rounded-2xl border border-white/5 p-6 space-y-5">
                        <div>
                            <h2 className="text-xl font-semibold text-white tracking-tight leading-tight">
                                {activeOffer?.title}
                            </h2>
                            <span className="inline-flex items-center px-2.5 py-1 mt-2 rounded-full text-[10px] uppercase tracking-wider font-semibold bg-white/5 text-gray-400 border border-white/5">
                                {activeOffer?.source}
                            </span>
                        </div>

                        <div className="space-y-3 text-sm">
                            <div className="flex items-center gap-2 text-gray-300">
                                <Building2 className="w-4 h-4 text-gray-500" />
                                <span className="font-medium">
                                    {activeOffer?.company}
                                </span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                                <MapPin className="w-4 h-4 text-gray-500" />
                                {activeOffer?.location}
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                                <Briefcase className="w-4 h-4 text-gray-500" />
                                <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/5 text-xs">
                                    {activeOffer?.contract_type}
                                </span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                                <Calendar className="w-4 h-4 text-gray-500" />
                                {activeOffer?.published_date}
                            </div>
                        </div>

                        {activeOffer?.url && (
                            <a
                                href={activeOffer.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 text-blue-400 text-sm hover:text-blue-300 transition-colors cursor-pointer"
                            >
                                <ExternalLink className="w-3.5 h-3.5" />
                                Voir l&apos;offre originale
                            </a>
                        )}
                    </div>

                    {/* AI Generation Card */}
                    <div className="bg-gradient-to-br from-blue-500/10 to-indigo-500/5 rounded-2xl border border-blue-500/20 p-5 space-y-3">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-blue-400" />
                            <span className="text-sm font-semibold text-blue-300">
                                Génération IA
                            </span>
                        </div>
                        <p className="text-xs text-gray-400 leading-relaxed">
                            Le moteur IA analyse l'offre et génère une lettre de
                            motivation et un CV personnalisés. Vous pouvez
                            ensuite les éditer librement.
                        </p>
                        <button
                            onClick={() => {
                                setIsGenerating(true);
                                setTimeout(() => setIsGenerating(false), 2000);
                            }}
                            disabled={isGenerating}
                            className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer ${isGenerating
                                    ? "bg-blue-500/30 text-blue-300/50 cursor-not-allowed"
                                    : "bg-blue-600 text-white hover:bg-blue-500 hover:shadow-[0_0_15px_rgba(37,99,235,0.4)]"
                                }`}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Génération en cours...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4" />
                                    Régénérer les documents
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* RIGHT PANEL — Document Editor */}
                <div className="flex-1 flex flex-col bg-[#0a0a0a] rounded-2xl border border-white/5 overflow-hidden min-h-0">
                    {/* Tabs */}
                    <div className="flex items-center border-b border-white/5 bg-[#080808]">
                        <button
                            onClick={() => setActiveTab("cv")}
                            className={`flex items-center gap-2 px-6 py-3.5 text-sm font-medium transition-all cursor-pointer border-b-2 ${activeTab === "cv"
                                    ? "text-blue-400 border-blue-500 bg-blue-500/5"
                                    : "text-gray-400 border-transparent hover:text-gray-300 hover:bg-white/[0.02]"
                                }`}
                        >
                            <FileText className="w-4 h-4" />
                            CV Personnalisé
                        </button>
                        <button
                            onClick={() => setActiveTab("lm")}
                            className={`flex items-center gap-2 px-6 py-3.5 text-sm font-medium transition-all cursor-pointer border-b-2 ${activeTab === "lm"
                                    ? "text-blue-400 border-blue-500 bg-blue-500/5"
                                    : "text-gray-400 border-transparent hover:text-gray-300 hover:bg-white/[0.02]"
                                }`}
                        >
                            <Mail className="w-4 h-4" />
                            Lettre de Motivation
                        </button>

                        {/* Spacer */}
                        <div className="flex-1" />

                        {/* Export button */}
                        <button className="flex items-center gap-2 px-4 py-2 mr-3 rounded-lg text-sm font-medium bg-white text-black hover:bg-gray-200 transition-all cursor-pointer shadow-[0_0_15px_rgba(255,255,255,0.1)]">
                            <Download className="w-4 h-4" />
                            Exporter .docx
                        </button>
                    </div>

                    {/* Toolbar */}
                    <div className="flex items-center gap-1 px-4 py-2 border-b border-white/5 bg-[#080808]">
                        {[
                            { icon: Bold, label: "Gras" },
                            { icon: Italic, label: "Italique" },
                            { icon: Underline, label: "Souligné" },
                        ].map(({ icon: Icon, label }) => (
                            <button
                                key={label}
                                title={label}
                                className="p-2 rounded-md hover:bg-white/10 text-gray-400 hover:text-white transition-colors cursor-pointer"
                            >
                                <Icon className="w-4 h-4" />
                            </button>
                        ))}

                        <div className="w-px h-5 bg-white/10 mx-1" />

                        {[
                            { icon: AlignLeft, label: "Gauche" },
                            { icon: AlignCenter, label: "Centre" },
                            { icon: AlignRight, label: "Droite" },
                        ].map(({ icon: Icon, label }) => (
                            <button
                                key={label}
                                title={label}
                                className="p-2 rounded-md hover:bg-white/10 text-gray-400 hover:text-white transition-colors cursor-pointer"
                            >
                                <Icon className="w-4 h-4" />
                            </button>
                        ))}

                        <div className="w-px h-5 bg-white/10 mx-1" />

                        <button
                            title="Liste"
                            className="p-2 rounded-md hover:bg-white/10 text-gray-400 hover:text-white transition-colors cursor-pointer"
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Text Editor Area */}
                    <div className="flex-1 overflow-y-auto p-6 min-h-0">
                        <div className="max-w-2xl mx-auto">
                            <textarea
                                value={currentContent}
                                onChange={(e) =>
                                    setCurrentContent(e.target.value)
                                }
                                className="w-full h-full min-h-[500px] bg-transparent text-gray-200 text-sm leading-relaxed resize-none outline-none placeholder-gray-600 font-[inherit]"
                                placeholder={
                                    activeTab === "cv"
                                        ? "Votre CV personnalisé apparaîtra ici..."
                                        : "Votre lettre de motivation apparaîtra ici..."
                                }
                                spellCheck={false}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ─── Template Generators ─────────────────────────────────────────────────────

function generateLmTemplate(offer: JobOffer): string {
    return `                                                           [Votre Prénom NOM]
                                                           [Votre adresse email]
                                                           [Votre téléphone]

                                                           ${new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}

À l'attention du service Recrutement
${offer.company}
${offer.location}

Objet : Candidature au poste de ${offer.title} — ${offer.contract_type}

Madame, Monsieur,

Actuellement à la recherche de nouvelles opportunités professionnelles, j'ai découvert avec un vif intérêt votre offre de ${offer.title} chez ${offer.company}, et je souhaite vous faire part de ma candidature.

[Paragraphe 1 — Présentez-vous et expliquez pourquoi ce poste vous intéresse. Mettez en avant votre compréhension du rôle et de l'entreprise ${offer.company}.]

[Paragraphe 2 — Décrivez vos compétences clés et expériences pertinentes en lien avec le poste de ${offer.title}. Donnez des exemples concrets de réalisations.]

[Paragraphe 3 — Expliquez votre valeur ajoutée pour l'équipe et votre motivation à rejoindre ${offer.company} à ${offer.location}.]

Dans l'attente de votre retour, je reste disponible pour un entretien à votre convenance. Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.

[Votre Prénom NOM]`;
}

function generateCvTemplate(offer: JobOffer): string {
    return `═══════════════════════════════════════════════════
                    [VOTRE PRÉNOM NOM]
             [votre.email@exemple.com] | [06 XX XX XX XX]
                  [Ville, France] | [LinkedIn]
═══════════════════════════════════════════════════

PROFIL PROFESSIONNEL
────────────────────
[Résumé de 2-3 lignes de votre profil, adapté au poste de ${offer.title} chez ${offer.company}. Mettez en avant vos compétences principales et votre expérience dans le domaine.]


EXPÉRIENCES PROFESSIONNELLES
─────────────────────────────

▸ [Poste Occupé] — [Entreprise]
  📅 [Dates] │ 📍 [Lieu]
  • [Réalisation clé #1 — Utilisez des chiffres et résultats concrets]
  • [Réalisation clé #2 — En lien avec les compétences demandées pour ${offer.title}]
  • [Réalisation clé #3]

▸ [Poste Occupé] — [Entreprise]
  📅 [Dates] │ 📍 [Lieu]
  • [Réalisation clé #1]
  • [Réalisation clé #2]


FORMATION
─────────
▸ [Diplôme] — [École / Université]
  📅 [Année] │ 📍 [Lieu]

▸ [Diplôme] — [École / Université]
  📅 [Année] │ 📍 [Lieu]


COMPÉTENCES
───────────
Techniques : [Compétence 1, Compétence 2, Compétence 3]
Outils     : [Outil 1, Outil 2, Outil 3]
Langues    : Français (natif), Anglais ([niveau])


CENTRES D'INTÉRÊT
──────────────────
[Intérêt 1] · [Intérêt 2] · [Intérêt 3]`;
}
