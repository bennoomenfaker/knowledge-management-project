from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter(prefix="/master-vic", tags=["Master VIC"])


class MasterVICInfo(BaseModel):
    name: str
    acronym: str
    year_launched: int
    coordinator: str
    coordinator_email: str
    institutions: List[str]
    objectives: List[str]
    modeles_theoriques: List[str]
    debouches: List[str]


class Competence(BaseModel):
    name: str
    description: str


class Module(BaseModel):
    name: str
    code: str
    credits: int
    description: str


class TimelineEvent(BaseModel):
    year: int
    event: str
    description: str


@router.get("/info", response_model=MasterVICInfo)
async def get_master_info():
    return MasterVICInfo(
        name="Master en Intelligence Compétitive et Veille Stratégique",
        acronym="VIC",
        year_launched=2014,
        coordinator="Afef Belghith",
        coordinator_email="afef.belghith@iscae.uma.tn",
        institutions=["ISCAE", "ESEN"],
        objectives=[
            "Développer les compétences en intelligence compétitive",
            "Maîtriser les techniques de veille stratégique",
            "Analyser les environnements complexes",
            "Gestion de l'information stratégique",
            "Passage d'une logique enseignée à une logique apprenante"
        ],
        modeles_theoriques=["SECI Model (Nonaka & Takeuchi)"],
        debouches=[
            "Analyste en intelligence économique",
            "Consultant en management de l'information",
            "Chargé de veille stratégique",
            "Chef de projet VIC",
            "Médiateur de veille"
        ]
    )


@router.get("/competences", response_model=List[Competence])
async def get_competences():
    return [
        Competence(
            name="Intelligence Compétitive",
            description="Collecte, analyse et diffusion de l'information stratégique"
        ),
        Competence(
            name="Veille Stratégique",
            description="Surveillance continue de l'environnement concurrentiel"
        ),
        Competence(
            name="Analyse des Environnements",
            description="Diagnostic stratégique des secteurs d'activité"
        ),
        Competence(
            name="Gestion de l'Information",
            description="Organisation et valorisation des données stratégiques"
        ),
        Competence(
            name="Management de la Connaissance",
            description="Créer, capturer, partager et utiliser les connaissances"
        ),
        Competence(
            name="Veille Technologique",
            description="Surveillance des évolutions technologiques"
        )
    ]


@router.get("/programme", response_model=List[Module])
async def get_programme():
    return [
        Module(name="fondamentaux de l'intelligence économique", code="VIC101", credits=4, description="Bases théoriques et概念uelles de l'IE"),
        Module(name="Méthodologies de Veille", code="VIC102", credits=4, description="Méthodes et outils de veille"),
        Module(name="Systèmes d'Information Stratégique", code="VIC103", credits=4, description="Architecture SI pour la VIC"),
        Module(name="Intelligence et Sécurité", code="VIC104", credits=3, description="Protection du patrimoine informationnel"),
        Module(name="Analyse des Données", code="VIC105", credits=4, description="Data analytics pour la VIC"),
        Module(name="Management de Projet VIC", code="VIC106", credits=3, description="Gestion de projet appliquée"),
        Module(name="Stage Professionnel", code="VIC107", credits=8, description="Stage en entreprise"),
        Module(name="Mémoire PFE", code="VIC108", credits=10, description="Projet de fin d'études")
    ]


@router.get("/timeline", response_model=List[TimelineEvent])
async def get_timeline():
    return [
        TimelineEvent(year=2014, event="Lancement du Master VIC", description="Partenariat ISCAE - ESEN"),
        TimelineEvent(year=2015, event="Première promotion", description="Première cohorte de diplômé.e.s"),
        TimelineEvent(year=2016, event="Partenariat international", description="Accords avec des universités européennes"),
        TimelineEvent(year=2017, event="Intégration outils IA", description="Introduction des technologies d'IA dans le програмme"),
        TimelineEvent(year=2018, event="Certification", description="Obtention de la certification nationale"),
        TimelineEvent(year=2019, event="Upgrade programme", description="Mise à niveau vers VIC 2.0"),
        TimelineEvent(year=2020, event="Digitalisation", description="Adaptation au contexte pandémique"),
        TimelineEvent(year=2021, event="Veille pandémie", description="Focus sur la veille sectorielle santé"),
        TimelineEvent(year=2022, event="AI & VIC", description="Intégration LLMs et IA générative"),
        TimelineEvent(year=2023, event="Expansion", description="Nouveaux partenariats industriels"),
        TimelineEvent(year=2024, event="10 ans VIC", description="Célébration du 10e anniversaire"),
        TimelineEvent(year=2025, event="Transformation digitale", description="Modernisation complète du програмme"),
        TimelineEvent(year=2026, event="Nouvelle ère", description="VIC - Intelligence Artificielle")
    ]


@router.get("/debouches", response_model=List[str])
async def get_debouches():
    return [
        "Analyste en intelligence économique",
        "Consultant en management de l'information",
        "Chargé de veille stratégique",
        "Chef de projet VIC",
        "Médiateur de veille",
        "Responsable Knowledge Management",
        "Analyste stratégique",
        "Consultant en transformation digitale"
    ]