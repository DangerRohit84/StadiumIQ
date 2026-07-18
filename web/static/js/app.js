/**
 * StadiumIQ v3.0 — AI Smart Stadium Assistant
 * Google Gemini 2.5 Flash powered with stunning UI
 */
(function () {
    'use strict';

    var API = '';
    var currentLang = 'en';
    var a11yMode = false;
    var crowdChart = null;
    var sentimentChart = null;

    // ─── i18n Translation Dictionary ─────────────────────────
    var I18N = {
        en: {
            loader_sub: 'Initializing AI Systems',
            nav_fan: 'Fan Experience', nav_cmd: 'Command Center',
            systems_online: 'Systems Online',
            hero_badge: 'FIFA World Cup 2026',
            hero_title_1: 'Your Personal', hero_title_2: 'AI Stadium', hero_title_3: 'Assistant',
            hero_sub: 'Navigate smarter. Experience better. Powered by Google Gemini 2.5 Flash.',
            stat_capacity: 'Capacity', stat_endpoints: 'API Endpoints', stat_languages: 'Languages', stat_tests: 'Tests Passing',
            ai_assistant: 'AI Assistant', ai_sub: 'Powered by Gemini 2.5 Flash', active: 'Active',
            greeting_title: 'Welcome to StadiumIQ!',
            greeting_sub: "I'm your AI-powered assistant for <strong>FIFA World Cup 2026</strong> at MetLife Stadium.",
            feat_nav: 'Navigation', feat_crowds: 'Live Crowds', feat_a11y: 'Accessibility', feat_eco: 'Sustainability', feat_match: 'Match Info', feat_transport: 'Transport',
            just_now: 'Just now',
            q_restroom: 'Restrooms', q_food: 'Food', q_crowds: 'Crowds', q_parking: 'Parking', q_accessible: 'Accessible', q_eco: 'Eco', q_schedule: 'Schedule', q_medical: 'Medical',
            chat_placeholder: 'Ask me anything about the stadium...',
            tab_crowd: 'Crowd', tab_map: 'Map', tab_transport: 'Transport', tab_eco: 'Eco',
            crowd_title: 'Real-Time Crowd Density', live: 'Live',
            map_title: 'Interactive Facility Map', transport_title: 'Transportation Hub', eco_title: 'Sustainability Dashboard',
            cmd_title: 'Operations Command Center', cmd_sub: 'Real-time stadium intelligence and operational analytics',
            cmd_crowd: 'Crowd Flow', cmd_sentiment: 'Fan Sentiment', cmd_risk: 'Risk Assessment',
            cmd_alerts: 'Live Alerts', cmd_staff: 'Staff Deployment', cmd_insights: 'AI Insights',
            footer_left: 'StadiumIQ v3.0 — Powered by Google Gemini 2.5 Flash',
            footer_right: 'FIFA World Cup 2026 — MetLife Stadium',
            toast_ready: 'StadiumIQ is ready! Ask me anything.',
            toast_lang: 'Language changed to',
        },
        es: {
            loader_sub: 'Inicializando sistemas de IA',
            nav_fan: 'Experiencia Fan', nav_cmd: 'Centro de Mando',
            systems_online: 'Sistemas en L\u00ednea',
            hero_badge: 'Copa Mundial FIFA 2026',
            hero_title_1: 'Tu Personal', hero_title_2: 'Estadio con IA', hero_title_3: 'Asistente',
            hero_sub: 'Navega mejor. Vive mejor. Impulsado por Google Gemini 2.5 Flash.',
            stat_capacity: 'Capacidad', stat_endpoints: 'Puntos API', stat_languages: 'Idiomas', stat_tests: 'Pruebas',
            ai_assistant: 'Asistente IA', ai_sub: 'Impulsado por Gemini 2.5 Flash', active: 'Activo',
            greeting_title: '\u00a1Bienvenido a StadiumIQ!',
            greeting_sub: 'Soy tu asistente con IA para la <strong>Copa Mundial FIFA 2026</strong> en MetLife Stadium.',
            feat_nav: 'Navegaci\u00f3n', feat_crowds: 'Multitudes', feat_a11y: 'Accesibilidad', feat_eco: 'Sostenibilidad', feat_match: 'Partidos', feat_transport: 'Transporte',
            just_now: 'Ahora',
            q_restroom: 'Ba\u00f1os', q_food: 'Comida', q_crowds: 'Multitudes', q_parking: 'Parking', q_accessible: 'Accesible', q_eco: 'Eco', q_schedule: 'Calendario', q_medical: 'M\u00e9dico',
            chat_placeholder: 'Preg\u00fabntame algo sobre el estadio...',
            tab_crowd: 'Multitud', tab_map: 'Mapa', tab_transport: 'Transporte', tab_eco: 'Eco',
            crowd_title: 'Densidad de Multitud en Tiempo Real', live: 'En Vivo',
            map_title: 'Mapa de Instalaciones', transport_title: 'Centro de Transporte', eco_title: 'Panel de Sostenibilidad',
            cmd_title: 'Centro de Mando de Operaciones', cmd_sub: 'Inteligencia del estadio en tiempo real y an\u00e1lisis operativo',
            cmd_crowd: 'Flujo de Multitud', cmd_sentiment: 'Sentimiento Fan', cmd_risk: 'Evaluaci\u00f3n de Riesgo',
            cmd_alerts: 'Alertas en Vivo', cmd_staff: 'Despliegue de Personal', cmd_insights: 'An\u00e1lisis IA',
            footer_left: 'StadiumIQ v3.0 — Impulsado por Google Gemini 2.5 Flash',
            footer_right: 'Copa Mundial FIFA 2026 — MetLife Stadium',
            toast_ready: '\u00a1StadiumIQ listo! Preg\u00fabtame algo.',
            toast_lang: 'Idioma cambiado a',
        },
        fr: {
            loader_sub: 'Initialisation des syst\u00e8mes IA',
            nav_fan: 'Exp\u00e9rience Fan', nav_cmd: 'Centre de Commande',
            systems_online: 'Syst\u00e8mes En Ligne',
            hero_badge: 'Coupe du Monde FIFA 2026',
            hero_title_1: 'Votre Personnel', hero_title_2: 'Stade IA', hero_title_3: 'Assistant',
            hero_sub: 'Naviguez plus intelligemment. Exp\u00e9rimentez mieux. Propuls\u00e9 par Google Gemini 2.5 Flash.',
            stat_capacity: 'Capacit\u00e9', stat_endpoints: 'Points API', stat_languages: 'Langues', stat_tests: 'Tests',
            ai_assistant: 'Assistant IA', ai_sub: 'Propuls\u00e9 par Gemini 2.5 Flash', active: 'Actif',
            greeting_title: 'Bienvenue sur StadiumIQ!',
            greeting_sub: 'Je suis votre assistant IA pour la <strong>Coupe du Monde FIFA 2026</strong> au MetLife Stadium.',
            feat_nav: 'Navigation', feat_crowds: 'Foules', feat_a11y: 'Accessibilit\u00e9', feat_eco: 'Durabilit\u00e9', feat_match: 'Matchs', feat_transport: 'Transport',
            just_now: 'Maintenant',
            q_restroom: 'Toilettes', q_food: 'Nourriture', q_crowds: 'Foules', q_parking: 'Parking', q_accessible: 'Accessible', q_eco: ' \u00c9co', q_schedule: 'Calendrier', q_medical: 'M\u00e9dical',
            chat_placeholder: 'Demandez-moi n\u2019importe quoi sur le stade...',
            tab_crowd: 'Foule', tab_map: 'Carte', tab_transport: 'Transport', tab_eco: '\u00c9co',
            crowd_title: 'Densit\u00e9 de Foule en Temps R\u00e9el', live: 'En Direct',
            map_title: 'Carte des Installations', transport_title: 'Hub de Transport', eco_title: 'Tableau de Durabilit\u00e9',
            cmd_title: 'Centre de Commande Op\u00e9rationsnel', cmd_sub: 'Intelligence du stade en temps r\u00e9el et analyses op\u00e9rationnelles',
            cmd_crowd: 'Flux de Foule', cmd_sentiment: 'Sentiment Fan', cmd_risk: '\u00c9valuation des Risques',
            cmd_alerts: 'Alertes en Direct', cmd_staff: 'D\u00e9ploiement du Personnel', cmd_insights: 'Analyses IA',
            footer_left: 'StadiumIQ v3.0 — Propuls\u00e9 par Google Gemini 2.5 Flash',
            footer_right: 'Coupe du Monde FIFA 2026 — MetLife Stadium',
            toast_ready: 'StadiumIQ pr\u00eat! Demandez-moi quelque chose.',
            toast_lang: 'Langue chang\u00e9e en',
        },
        de: {
            loader_sub: 'KI-Systeme werden initialisiert',
            nav_fan: 'Fan-Erfahrung', nav_cmd: 'Kommandozentrale',
            systems_online: 'Systeme Online',
            hero_badge: 'FIFA Weltmeisterschaft 2026',
            hero_title_1: 'Ihr Pers\u00f6nlicher', hero_title_2: 'KI-Stadion', hero_title_3: 'Assistent',
            hero_sub: 'Navigieren Sie intelligenter. Erleben Sie besser. Angetrieben von Google Gemini 2.5 Flash.',
            stat_capacity: 'Kapazit\u00e4t', stat_endpoints: 'API-Endpunkte', stat_languages: 'Sprachen', stat_tests: 'Tests',
            ai_assistant: 'KI-Assistent', ai_sub: 'Angetrieben von Gemini 2.5 Flash', active: 'Aktiv',
            greeting_title: 'Willkommen bei StadiumIQ!',
            greeting_sub: 'Ich bin Ihr KI-Assistent f\u00fcr die <strong>FIFA Weltmeisterschaft 2026</strong> im MetLife Stadium.',
            feat_nav: 'Navigation', feat_crowds: 'Mengen', feat_a11y: 'Barrierefreiheit', feat_eco: 'Nachhaltigkeit', feat_match: 'Spiele', feat_transport: 'Transport',
            just_now: 'Jetzt',
            q_restroom: 'Toiletten', q_food: 'Essen', q_crowds: 'Mengen', q_parking: 'Parkplatz', q_accessible: 'Barrierefrei', q_eco: '\u00d6ko', q_schedule: 'Zeitplan', q_medical: 'Medizinisch',
            chat_placeholder: 'Fragen Sie mich alles \u00fcber das Stadion...',
            tab_crowd: 'Menge', tab_map: 'Karte', tab_transport: 'Transport', tab_eco: '\u00d6ko',
            crowd_title: 'Echtzeit-Mengendichte', live: 'Live',
            map_title: 'Interaktive Einrichtungskarte', transport_title: 'Transportzentrum', eco_title: 'Nachhaltigkeits-Dashboard',
            cmd_title: 'Operations-Kommandozentrale', cmd_sub: 'Echtzeit-Stadionintelligenz und operative Analytik',
            cmd_crowd: 'Mengenfluss', cmd_sentiment: 'Fan-Stimmung', cmd_risk: 'Risikobewertung',
            cmd_alerts: 'Live-Warnungen', cmd_staff: 'Personaleinsatz', cmd_insights: 'KI-Einblicke',
            footer_left: 'StadiumIQ v3.0 — Angetrieben von Google Gemini 2.5 Flash',
            footer_right: 'FIFA Weltmeisterschaft 2026 — MetLife Stadium',
            toast_ready: 'StadiumIQ bereit! Fragen Sie mich alles.',
            toast_lang: 'Sprache ge\u00e4ndert zu',
        },
        zh: {
            loader_sub: 'AI\u7cfb\u7edf\u521d\u59cb\u5316\u4e2d',
            nav_fan: '\u7c89\u4e1d\u4f53\u9a8c', nav_cmd: '\u6307\u6325\u4e2d\u5fc3',
            systems_online: '\u7cfb\u7edf\u5728\u7ebf',
            hero_badge: '2026\u5e74FIFA\u4e16\u754c\u676f',
            hero_title_1: '\u60a8\u7684\u4e2a\u4eba', hero_title_2: 'AI\u667a\u80fd\u4f53\u80b2\u573a', hero_title_3: '\u52a9\u624b',
            hero_sub: '\u667a\u80fd\u5bfc\u822a\u3002\u66f4\u597d\u4f53\u9a8c\u3002\u7531Google Gemini 2.5 Flash\u9a71\u52a8\u3002',
            stat_capacity: '\u5bb9\u91cf', stat_endpoints: 'API\u7aef\u70b9', stat_languages: '\u8bed\u8a00', stat_tests: '\u6d4b\u8bd5',
            ai_assistant: 'AI\u52a9\u624b', ai_sub: '\u7531Gemini 2.5 Flash\u63d0\u4f9b\u652f\u6301', active: '\u6d3b\u8dc3',
            greeting_title: '\u6b22\u8fce\u4f7f\u7528StadiumIQ\uff01',
            greeting_sub: '\u6211\u662f\u60a8\u7684AI\u52a9\u624b\uff0c\u4e13\u4e3a<strong>2026\u5e74FIFA\u4e16\u754c\u676f</strong>\u800c\u8bbe\u8ba1\u3002',
            feat_nav: '\u5bfc\u822a', feat_crowds: '\u4eba\u7fa4', feat_a11y: '\u65e0\u969c\u788d', feat_eco: '\u53ef\u6301\u7eed', feat_match: '\u6bd4\u8d5b\u4fe1\u606f', feat_transport: '\u4ea4\u901a',
            just_now: '\u521a\u521a',
            q_restroom: '\u6d17\u624b\u95f4', q_food: '\u98df\u7269', q_crowds: '\u4eba\u7fa4', q_parking: '\u505c\u8f66', q_accessible: '\u65e0\u969c\u788d', q_eco: '\u73af\u4fdd', q_schedule: '\u65e5\u7a0b', q_medical: '\u533b\u7597',
            chat_placeholder: '\u95ee\u6211\u4efb\u4f55\u5173\u4e8e\u4f53\u80b2\u573a\u7684\u95ee\u9898...',
            tab_crowd: '\u4eba\u7fa4', tab_map: '\u5730\u56fe', tab_transport: '\u4ea4\u901a', tab_eco: '\u73af\u4fdd',
            crowd_title: '\u5b9e\u65f6\u4eba\u7fa4\u5bc6\u5ea6', live: '\u5b9e\u65f6',
            map_title: '\u4ea4\u4e92\u5f0f\u8bbe\u65bd\u5730\u56fe', transport_title: '\u4ea4\u901a\u4e2d\u5fc3', eco_title: '\u53ef\u6301\u7eed\u53d1\u5c55\u63a7\u5236\u53f0',
            cmd_title: '\u8fd0\u8425\u6307\u6325\u4e2d\u5fc3', cmd_sub: '\u5b9e\u65f6\u4f53\u80b2\u573a\u667a\u80fd\u5206\u6790',
            cmd_crowd: '\u4eba\u7fa4\u6d41\u52a8', cmd_sentiment: '\u7c89\u4e1d\u60c5\u611f', cmd_risk: '\u98ce\u9669\u8bc4\u4f30',
            cmd_alerts: '\u5b9e\u65f6\u8b66\u62a5', cmd_staff: '\u5de5\u4f5c\u4eba\u5458\u90e8\u7f72', cmd_insights: 'AI\u6d1e\u5bdf',
            footer_left: 'StadiumIQ v3.0 \u2014 \u7531Google Gemini 2.5 Flash\u9a71\u52a8',
            footer_right: '2026\u5e74FIFA\u4e16\u754c\u676f \u2014 MetLife\u4f53\u80b2\u573a',
            toast_ready: 'StadiumIQ\u5df2\u5c31\u7eea\uff01\u95ee\u6211\u4efb\u4f55\u95ee\u9898\u3002',
            toast_lang: '\u8bed\u8a00\u5df2\u66f4\u6539\u4e3a',
        },
        ja: {
            loader_sub: 'AI\u30b7\u30b9\u30c6\u30e0\u521d\u59cb\u5316\u4e2d',
            nav_fan: '\u30d5\u30a1\u30f3\u4f53\u9a13', nav_cmd: '\u30b3\u30de\u30f3\u30c9\u30bb\u30f3\u30bf\u30fc',
            systems_online: '\u30b7\u30b9\u30c6\u30e0\u30aa\u30f3\u30e9\u30a4\u30f3',
            hero_badge: 'FIFA\u30ef\u30fc\u30eb\u30c9\u30ab\u30c3\u30d72026',
            hero_title_1: '\u3042\u306a\u305f\u306e\u30da\u30fc\u30b7\u30e3\u30eb', hero_title_2: 'AI\u30b9\u30bf\u30b8\u30a2\u30e2', hero_title_3: '\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8',
            hero_sub: '\u30b9\u30de\u30fc\u30c8\u306b\u30ca\u30d3\u30b2\u30fc\u30b7\u30e7\u30f3\u3002\u3088\u308a\u826f\u3044\u4f53\u9a13\u3002Google Gemini 2.5 Flash\u3067\u9a71\u52d5\u3002',
            stat_capacity: '\u53ce\u5bb9', stat_endpoints: 'API\u30a8\u30f3\u30dd\u30a4\u30f3\u30c8', stat_languages: '\u8a00\u8a9e', stat_tests: '\u30c6\u30b9\u30c8',
            ai_assistant: 'AI\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8', ai_sub: 'Gemini 2.5 Flash\u3067\u30d1\u30ef\u30fc', active: '\u30a2\u30af\u30c6\u30a3\u30d6',
            greeting_title: 'StadiumIQ\u3078\u3088\u3046\u3053\u305d\uff01',
            greeting_sub: '<strong>FIFA\u30ef\u30fc\u30eb\u30c9\u30ab\u30c3\u30d72026</strong>\u306eAI\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8\u3067\u3059\u3002',
            feat_nav: '\u30ca\u30d3\u30b2\u30fc\u30b7\u30e7\u30f3', feat_crowds: '\u4eba\u6ce2', feat_a11y: '\u30a2\u30af\u30bb\u30b7\u30d3\u30ea\u30c6\u30a3', feat_eco: '\u6301\u7d9a\u53ef\u80fd', feat_match: '\u8a66\u5408', feat_transport: '\u4ea4\u901a',
            just_now: '\u4eca\u3059\u3050',
            q_restroom: '\u30c8\u30a4\u30ec', q_food: '\u98df\u4e8b', q_crowds: '\u4eba\u6ce2', q_parking: '\u99d0\u8eeb\u5834', q_accessible: '\u30a2\u30af\u30bb\u30b7\u30d3\u30eb', q_eco: '\u30a8\u30b3', q_schedule: '\u65e5\u7a0b', q_medical: '\u533b\u7642',
            chat_placeholder: '\u30b9\u30bf\u30b8\u30a2\u306b\u95a2\u3059\u308b\u4f55\u3067\u3082\u304a\u554f\u3044\u5408\u308f\u305b...',
            tab_crowd: '\u4eba\u6ce2', tab_map: '\u5730\u56f3', tab_transport: '\u4ea4\u901a', tab_eco: '\u30a8\u30b3',
            crowd_title: '\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u4eba\u6ce2\u5bc6\u5ea6', live: '\u30e9\u30a4\u30d6',
            map_title: '\u65bd\u8a2d\u30de\u30c3\u30d7', transport_title: '\u4ea4\u901a\u30cf\u30d6', eco_title: '\u6301\u7d9a\u53ef\u80fd\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9',
            cmd_title: '\u904b\u55b6\u30b3\u30de\u30f3\u30c9\u30bb\u30f3\u30bf\u30fc', cmd_sub: '\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30b9\u30bf\u30b8\u30a2\u60c5\u5831\u3068\u904b\u55b6\u5206\u6790',
            cmd_crowd: '\u4eba\u6ce2\u30d5\u30ed\u30fc', cmd_sentiment: '\u30d5\u30a1\u30f3\u611f\u60c5', cmd_risk: '\u30ea\u30b9\u30af\u8a55\u4fa1',
            cmd_alerts: '\u30e9\u30a4\u30d6\u30a2\u30e9\u30fc\u30c8', cmd_staff: '\u30b9\u30bf\u30c3\u30d5\u914d\u7f6e', cmd_insights: 'AI\u6d1e\u5bdf',
            footer_left: 'StadiumIQ v3.0 \u2014 Google Gemini 2.5 Flash\u3067\u9a71\u52d5',
            footer_right: 'FIFA\u30ef\u30fc\u30eb\u30c9\u30ab\u30c3\u30d72026 \u2014 MetLife\u30b9\u30bf\u30b8\u30a2',
            toast_ready: 'StadiumIQ\u6e96\u5099\u5b8c\u4e86\uff01\u4f55\u3067\u3082\u304a\u554f\u3044\u5408\u308f\u305b\u304f\u3060\u3055\u3044\u3002',
            toast_lang: '\u8a00\u8a9e\u3092\u5909\u66f4\u3057\u307e\u3057\u305f',
        },
        ko: {
            loader_sub: 'AI \uc2dc\uc2a4\ud15c \ucd08\uc2dc\ud655',
            nav_fan: '\ud32c \ucee8\ud14c\uc2a4', nav_cmd: '\ucee4\ub2e4\uc778\uc5d0\ub4dc',
            systems_online: '\uc2dc\uc2a4\ud15c \uc624\ub77c\uc778',
            hero_badge: 'FIFA \uc6d4\ub4dc\ucee8\ud504 2026',
            hero_title_1: '\ub2f9\uc2e0\uc758', hero_title_2: 'AI \uc2a4\ud0c0\uc778', hero_title_3: '\ub3c4\uc6c0',
            hero_sub: '\ub354 \uba87\ubc88 \ub113\uac8c \ub124\uc774\ubc84\ud558\uc138\uc694. Google Gemini 2.5 Flash\uc5d0 \ub77c\uc6b0\ub294.',
            stat_capacity: '\uc6a9\ub7c8', stat_endpoints: 'API \uc5d4\ud305\ud2b8', stat_languages: '\uc5b8\uc5b4', stat_tests: '\ud14c\uc2a4\ud2b8',
            ai_assistant: 'AI \uc2dc\uc2a4\ud15c', ai_sub: 'Gemini 2.5 Flash \uae30\uc220', active: '\ud65c\uc601',
            greeting_title: 'StadiumIQ\uc5d0 \uc624\uc2e0 \uac83\uc744 \ud658\uc601\ud569\ub2c8\ub2e4!',
            greeting_sub: '<strong>FIFA \uc6d4\ub4dc\ucee8\ud504 2026</strong> \uc2dc\uc2a4\ud15c \uc2dc\uc2a4\ud15c \uc2dc\uc2a4\ud15c \ub3c4\uc6c0\uc785\ub2c8\ub2e4.',
            feat_nav: '\ub124\uc774\ubc84\uc774\uc158', feat_crowds: '\uc778\ud0a4', feat_a11y: '\ubb34\uc5e7\ud558\uc9c0 \uc5c6\uc774', feat_eco: '\uc9c0\uc18d\uc131', feat_match: '\uacbd\uae30', feat_transport: '\uac70\ud1b5',
            just_now: '\uc790\uae30',
            q_restroom: '\uc708\ub300\uc2dc\uacfc', q_food: '\uc2f8\ubc00', q_crowds: '\uc778\ud0a4', q_parking: '\uc8fc\ucc28', q_accessible: '\ubb34\uc5e7\ud558\uc9c0 \uc5c6\uc774', q_eco: '\uc5d0\ucf54', q_schedule: '\uc77c\uc815', q_medical: '\uc758\ub8cc',
            chat_placeholder: '\uc2a4\ud0c0\uc778\uc5d0 \uad00\ud55c \ubb3c\uc5b4\ub4e0 \ubb3c\uc5b4\ubcf4\uc138\uc694...',
            tab_crowd: '\uc778\ud0a4', tab_map: '\ub514\uc9c0\ud130', tab_transport: '\uac70\ud1b5', tab_eco: '\uc5d0\ucf54',
            crowd_title: '\uc2e4\uc2dc\uac04 \uc778\ud0a4 \ubc00\ub3c4', live: '\uc2e4\uc2dc\uac04',
            map_title: '\uc2dc\uc124 \ub9f5\ud504', transport_title: '\uac70\ud1b5 \ud5e9', eco_title: '\uc9c0\uc18d\uc131 \ub300\uc2dc\ubc84\ub4dc',
            cmd_title: '\uc6b4\uc601 \ucee4\ub2e4\uc778\uc5d0\ub4dc', cmd_sub: '\uc2e4\uc2dc\uac04 \uc2a4\ud0c0\uc778 \uc815\ubcf8\ubd84\uc11d',
            cmd_crowd: '\uc778\ud0a4 \ud751\ub4dd', cmd_sentiment: '\ud32c \uac10\uc815', cmd_risk: '\uc6d0\ud558 \ud3c9\uac00',
            cmd_alerts: '\uc2e4\uc2dc\uac04 \uacfc\ud558', cmd_staff: '\uc7a5\uad7c \ubd84\uc0b0', cmd_insights: 'AI \ub9cc\ub828',
            footer_left: 'StadiumIQ v3.0 \u2014 Google Gemini 2.5 Flash \uc5d0 \ub77c\uc6b0\ub294',
            footer_right: 'FIFA \uc6d4\ub4dc\ucee8\ud504 2026 \u2014 MetLife \uc2a4\ud0c0\uc778',
            toast_ready: 'StadiumIQ \uc900\ube44 \uc644\ub8cc! \ubb3c\uc5b4\ub4e0 \ubb3c\uc5b4\ubcf4\uc138\uc694.',
            toast_lang: '\uc5b8\uc5b4\uac00 \ubcc0\uacbd\ub418\uc5c8\uc2b5\ub2c8\ub2e4',
        },
        pt: {
            loader_sub: 'Inicializando sistemas de IA',
            nav_fan: 'Experi\u00eancia do F\u00e3', nav_cmd: 'Centro de Comando',
            systems_online: 'Sistemas Online',
            hero_badge: 'Copa do Mundo FIFA 2026',
            hero_title_1: 'Seu Pessoal', hero_title_2: 'Est\u00e1dio IA', hero_title_3: 'Assistente',
            hero_sub: 'Navegue melhor. Experiencie melhor. Powered by Google Gemini 2.5 Flash.',
            stat_capacity: 'Capacidade', stat_endpoints: 'Endpoints API', stat_languages: 'Idiomas', stat_tests: 'Testes',
            ai_assistant: 'Assistente IA', ai_sub: 'Powered by Gemini 2.5 Flash', active: 'Ativo',
            greeting_title: 'Bem-vindo ao StadiumIQ!',
            greeting_sub: 'Sou seu assistente de IA para a <strong>Copa do Mundo FIFA 2026</strong> no MetLife Stadium.',
            feat_nav: 'Navega\u00e7\u00e3o', feat_crowds: 'Multid\u00e3o', feat_a11y: 'Acessibilidade', feat_eco: 'Sustentabilidade', feat_match: 'Jogos', feat_transport: 'Transporte',
            just_now: 'Agora',
            q_restroom: 'Banheiros', q_food: 'Comida', q_crowds: 'Multid\u00e3o', q_parking: 'Estacionamento', q_accessible: 'Acess\u00edvel', q_eco: 'Eco', q_schedule: 'Calend\u00e1rio', q_medical: 'M\u00e9dico',
            chat_placeholder: 'Pergunte qualquer coisa sobre o est\u00e1dio...',
            tab_crowd: 'Multid\u00e3o', tab_map: 'Mapa', tab_transport: 'Transporte', tab_eco: 'Eco',
            crowd_title: 'Densidade de Multid\u00e3o em Tempo Real', live: 'Ao Vivo',
            map_title: 'Mapa de Instala\u00e7\u00f5es', transport_title: 'Hub de Transporte', eco_title: 'Painel de Sustentabilidade',
            cmd_title: 'Centro de Comando de Opera\u00e7\u00f5es', cmd_sub: 'Intelig\u00eancia do est\u00e1dio em tempo real e an\u00e1lises operacionais',
            cmd_crowd: 'Fluxo de Multid\u00e3o', cmd_sentiment: 'Sentimento do F\u00e3', cmd_risk: 'Avalia\u00e7\u00e3o de Risco',
            cmd_alerts: 'Alertas ao Vivo', cmd_staff: 'Implanta\u00e7\u00e3o de Equipe', cmd_insights: 'An\u00e1lises IA',
            footer_left: 'StadiumIQ v3.0 \u2014 Powered by Google Gemini 2.5 Flash',
            footer_right: 'Copa do Mundo FIFA 2026 \u2014 MetLife Stadium',
            toast_ready: 'StadiumIQ pronto! Pergunte qualquer coisa.',
            toast_lang: 'Idioma alterado para',
        },
        hi: {
            loader_sub: 'AI \u0938\u093f\u0938\u094d\u091f\u092e \u0915\u094b \u0907\u0928\u093f\u0936\u0932\u093f\u091f \u0939\u094b \u0930\u0939\u093e \u0939\u0948',
            nav_fan: '\u092a\u094d\u0930\u0936\u0902\u0938\u0915 \u0905\u0928\u0941\u092d\u0935', nav_cmd: '\u0915\u092e\u093e\u0902\u0921 \u0938\u0947\u0902\u091f\u0930',
            systems_online: '\u0938\u093f\u0938\u094d\u091f\u092e \u0911\u0928\u0932\u093e\u0907\u0928',
            hero_badge: 'FIFA \u0935\u0930\u094d\u0932\u094d\u0921 \u0915\u092a 2026',
            hero_title_1: '\u0906\u092a\u0915\u093e \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u0917\u0935', hero_title_2: 'AI \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e', hero_title_3: '\u0938\u0939\u093e\u092f\u0915',
            hero_sub: '\u0938\u092e\u0902\u0926\u093e\u0928 \u0928\u0947\u0935\u093f\u0917\u0947\u0936\u0928\u0964 \u092c\u0947\u0939\u0924\u0930 \u0905\u0928\u0941\u092d\u0935\u0964 Google Gemini 2.5 Flash \u0938\u0947 \u091a\u0932\u093e\u092f\u093e \u0917\u092f\u093e\u0964',
            stat_capacity: '\u0915\u094d\u0937\u092e\u0924\u093e', stat_endpoints: 'API \u0907\u0902\u091f\u091f', stat_languages: '\u092d\u093e\u0937\u093e\u0913\u0902', stat_tests: '\u092a\u0930\u0940\u0915\u094d\u0937\u093e',
            ai_assistant: 'AI \u0938\u0939\u093e\u092f\u0915', ai_sub: 'Gemini 2.5 Flash \u0938\u0947 \u0938\u0902\u091a\u093e\u0932\u093f\u0924', active: '\u0938\u0915\u094d\u0930\u093f\u092f',
            greeting_title: 'StadiumIQ \u092e\u0947\u0902 \u0906\u092a\u0915\u093e \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948!',
            greeting_sub: '\u092e\u0948\u0902 <strong>FIFA \u0935\u0930\u094d\u0932\u094d\u0921 \u0915\u092a 2026</strong> \u0915\u0947 \u0932\u093f\u090f \u0906\u092a\u0915\u093e AI \u0938\u0939\u093e\u092f\u0915 \u0939\u0942\u0902\u0964',
            feat_nav: '\u0928\u0947\u0935\u093f\u0917\u0947\u0936\u0928', feat_crowds: '\u092d\u0940\u0921\u093c', feat_a11y: '\u0905\u0915\u094d\u0938\u0947\u0936\u092c\u093f\u0932\u093f\u091f\u0940', feat_eco: '\u091f\u093f\u0915\u093e\u094b', feat_match: '\u092e\u0948\u091a', feat_transport: '\u092a\u0930\u093f\u0935\u0939\u093e\u0928',
            just_now: '\u0905\u092d\u0940',
            q_restroom: '\u0936\u094c\u091a\u093e\u0918\u0930', q_food: '\u0916\u093e\u0928\u093e', q_crowds: '\u092d\u0940\u0921\u093c', q_parking: '\u092a\u093e\u0930\u094d\u0915\u093f\u0902\u0917', q_accessible: '\u0938\u0941\u0932\u092d', q_eco: '\u091f\u093f\u0915\u093e\u094b', q_schedule: '\u0936\u0947\u0921\u0942\u0932', q_medical: '\u092e\u0947\u0921\u093f\u0915\u0932',
            chat_placeholder: '\u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e \u0915\u0947 \u092c\u093e\u0930\u0947 \u0915\u0941\u091b \u092d\u0940 \u092a\u0942\u091b\u0947\u0902...',
            tab_crowd: '\u092d\u0940\u0921\u093c', tab_map: '\u0928\u0915\u094d\u0936\u093e', tab_transport: '\u092a\u0930\u093f\u0935\u0939\u093e\u0928', tab_eco: '\u091f\u093f\u0915\u093e\u094b',
            crowd_title: '\u0930\u093f\u092f\u0932\u091f\u093e\u0907\u092e \u092d\u0940\u0921\u093c \u0917\u0939\u0930\u093e\u0907', live: '\u0932\u093e\u0907\u0935',
            map_title: '\u0907\u0902\u091f\u0930\u0947\u0915\u094d\u091f\u093f\u0935 \u0938\u0941\u0935\u093f\u0927\u093e \u092e\u093e\u0928\u091a\u093f\u0924\u0930', transport_title: '\u092a\u0930\u093f\u0935\u0939\u093e\u0928 \u0939\u092c', eco_title: '\u091f\u093f\u0915\u093e\u094b \u0921\u0948\u0936\u092c\u094b\u0930\u094d\u0921',
            cmd_title: '\u0913\u092a\u0930\u0947\u0936\u0902\u0938 \u0915\u092e\u093e\u0902\u0921 \u0938\u0947\u0902\u091f\u0930', cmd_sub: '\u0930\u093f\u092f\u0932\u091f\u093e\u0907\u092e \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0914\u0930 \u0935\u094d\u092f\u0935\u0938\u093e\u092f\u0940 \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923',
            cmd_crowd: '\u092d\u0940\u0921\u093c \u092a\u094d\u0930\u0935\u093e\u0939', cmd_sentiment: '\u092a\u094d\u0930\u0936\u0902\u0938\u0915 \u092d\u093e\u0935\u0928\u093e', cmd_risk: '\u091c\u094b\u0916\u093f\u092e \u092e\u0942\u0932\u094d\u092f\u093e\u0902',
            cmd_alerts: '\u0932\u093e\u0907\u0935 \u0905\u0932\u0930\u094d\u091f', cmd_staff: '\u0915\u0930\u094d\u092e\u091a\u093e\u0930\u093f \u0924\u0948\u0928\u093e\u0924\u094d', cmd_insights: 'AI \u0905\u0902\u0924\u0930\u094d\u0937\u093e\u0923',
            footer_left: 'StadiumIQ v3.0 \u2014 Google Gemini 2.5 Flash \u0938\u0947 \u0938\u0902\u091a\u093e\u0932\u093f\u0924',
            footer_right: 'FIFA \u0935\u0930\u094d\u0932\u094d\u0921 \u0915\u092a 2026 \u2014 MetLife \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e',
            toast_ready: 'StadiumIQ \u0924\u0948\u092f\u093e\u0930 \u0939\u0948! \u0915\u0941\u0924\u0940 \u092d\u0940 \u092a\u0942\u091b\u0947\u0902\u0964',
            toast_lang: '\u092d\u093e\u0937\u093e \u092c\u0926\u0932 \u0915\u0930 \u0926\u093f\u092f\u093e',
        },
    };

    // ─── Init ────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        initParticles();
        animateCounters();
        translateUI(currentLang);

        setTimeout(function () {
            document.getElementById('app-loader').classList.add('hidden');
            var t = I18N[currentLang] || I18N.en;
            showToast(t.toast_ready, 'success');
        }, 2200);

        loadCrowdData();
        loadTransportData();
        loadEcoData();
        loadFacilityMap();
        setupChat();
        setupTabs();

        document.getElementById('lang-select').addEventListener('change', function () {
            currentLang = this.value;
            translateUI(currentLang);
            showToast((I18N[currentLang] || I18N.en).toast_lang + ' ' + this.options[this.selectedIndex].text, 'info');
        });

        setInterval(refreshCrowdData, 6000);
    });

    // ─── Canvas Particle System ──────────────────────────────
    function initParticles() {
        var canvas = document.getElementById('particles-canvas');
        if (!canvas) return;
        var ctx = canvas.getContext('2d');
        var particles = [];
        var particleCount = 60;
        var colors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        function Particle() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.3;
            this.vy = (Math.random() - 0.5) * 0.3;
            this.radius = Math.random() * 2 + 0.5;
            this.color = colors[Math.floor(Math.random() * colors.length)];
            this.alpha = Math.random() * 0.4 + 0.1;
            this.pulse = Math.random() * Math.PI * 2;
        }

        for (var i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (var i = 0; i < particles.length; i++) {
                var p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.pulse += 0.02;

                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;

                var currentAlpha = p.alpha + Math.sin(p.pulse) * 0.15;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = Math.max(0.05, currentAlpha);
                ctx.fill();

                for (var j = i + 1; j < particles.length; j++) {
                    var p2 = particles[j];
                    var dx = p.x - p2.x;
                    var dy = p.y - p2.y;
                    var dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = p.color;
                        ctx.globalAlpha = (1 - dist / 150) * 0.08;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
            ctx.globalAlpha = 1;
            requestAnimationFrame(draw);
        }
        draw();
    }

    // ─── Animated Counters ──────────────────────────────────
    function animateCounters() {
        var counters = document.querySelectorAll('.stat-value[data-count]');
        counters.forEach(function (el) {
            var target = parseInt(el.getAttribute('data-count'), 10);
            var duration = 2000;
            var startTime = null;

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                var progress = Math.min((timestamp - startTime) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                var current = Math.floor(eased * target);
                el.textContent = current.toLocaleString();
                if (progress < 1) requestAnimationFrame(step);
            }
            setTimeout(function () { requestAnimationFrame(step); }, 800);
        });
    }

    // ─── UI Translation System ───────────────────────────────
    function translateUI(lang) {
        var t = I18N[lang] || I18N.en;
        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            var key = el.getAttribute('data-i18n');
            if (t[key]) el.innerHTML = t[key];
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            var key = el.getAttribute('data-i18n-placeholder');
            if (t[key]) el.placeholder = t[key];
        });
        document.documentElement.lang = lang;
    }

    // ─── Toast Notifications ─────────────────────────────────
    window.showToast = function (message, type) {
        type = type || 'info';
        var container = document.getElementById('toast-container');
        if (!container) return;

        var toast = document.createElement('div');
        toast.className = 'toast ' + type;

        var icons = { success: 'fa-check-circle', warning: 'fa-exclamation-triangle', error: 'fa-times-circle', info: 'fa-info-circle' };
        toast.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + ' toast-icon"></i><span>' + message + '</span>';
        container.appendChild(toast);

        setTimeout(function () {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(function () { toast.remove(); }, 300);
        }, 3500);
    };

    // ─── View Switching ──────────────────────────────────────
    window.switchView = function (view) {
        document.querySelectorAll('.view').forEach(function (v) { v.classList.remove('active'); });
        var target = document.getElementById('view-' + view);
        if (target) target.classList.add('active');
        document.querySelectorAll('.nav-pill').forEach(function (b) {
            b.classList.toggle('active', b.dataset.view === view);
        });
        if (view === 'command') loadCommandCenter();
    };

    // ─── Tab Switching ───────────────────────────────────────
    function setupTabs() {
        document.querySelectorAll('.panel-tab').forEach(function (tab) {
            tab.addEventListener('click', function () {
                var name = this.dataset.tab;
                switchInfoTab(name);
            });
        });
    }

    window.switchInfoTab = function (name) {
        document.querySelectorAll('.panel-tab').forEach(function (t) {
            t.classList.toggle('active', t.dataset.tab === name);
        });
        document.querySelectorAll('.tab-content').forEach(function (p) { p.classList.remove('active'); });
        var panel = document.getElementById('tab-' + name);
        if (panel) panel.classList.add('active');
    };

    // ─── Accessibility Toggle ────────────────────────────────
    window.toggleAccessibility = function () {
        a11yMode = !a11yMode;
        document.body.classList.toggle('a11y', a11yMode);
        document.getElementById('a11y-btn').classList.toggle('active', a11yMode);
        showToast(a11yMode ? 'Accessibility mode enabled' : 'Accessibility mode disabled', 'info');
    };

    // ─── Chat System ─────────────────────────────────────────
    function setupChat() {
        document.getElementById('chat-form').addEventListener('submit', function (e) {
            e.preventDefault();
            var input = document.getElementById('chat-input');
            var msg = input.value.trim();
            if (!msg) return;
            sendChat(msg);
            input.value = '';
        });
    }

    window.sendQuick = function (msg) { sendChat(msg); };

    function sendChat(message) {
        appendMsg('user', message);
        showTyping();

        fetch(API + '/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, language: currentLang, fan_id: 'web-user' })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            removeTyping();
            if (data.status === 'success') {
                appendMsg('bot', data.data.response, data.data.latency_ms, data.data.source);
            } else {
                appendMsg('bot', 'Sorry, something went wrong. Please try again.');
            }
        })
        .catch(function () {
            removeTyping();
            appendMsg('bot', 'Connection error. Please check your network.');
        });
    }

    function appendMsg(type, content, latency, source) {
        var container = document.getElementById('chat-messages');
        var div = document.createElement('div');
        div.className = 'msg ' + type;

        var icon = type === 'bot' ? 'fa-robot' : 'fa-user';
        var time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        var footer = '<span class="msg-time">' + time;
        if (latency) footer += ' \u00b7 ' + source + ' \u00b7 ' + latency + 'ms';
        footer += '</span>';

        div.innerHTML =
            '<div class="msg-avatar"><i class="fas ' + icon + '"></i></div>' +
            '<div class="msg-body"><div class="msg-bubble">' + formatMd(content) + '</div>' + footer + '</div>';

        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function showTyping() {
        var container = document.getElementById('chat-messages');
        var div = document.createElement('div');
        div.className = 'msg bot typing';
        div.id = 'typing-indicator';
        div.innerHTML =
            '<div class="msg-avatar"><i class="fas fa-robot"></i></div>' +
            '<div class="msg-body"><div class="msg-bubble">' +
            '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>' +
            '</div></div>';
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function removeTyping() {
        var el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    function formatMd(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\|(.+)\|/g, function (match) {
                var cells = match.split('|').filter(function (c) { return c.trim(); });
                if (cells.length >= 2) {
                    return '<div style="display:grid;grid-template-columns:repeat(' + cells.length + ',1fr);gap:2px;margin:3px 0;font-size:0.72rem">' +
                        cells.map(function (c) { return '<span style="padding:3px 5px;background:rgba(255,255,255,0.04);border-radius:4px;border:1px solid rgba(255,255,255,0.06)">' + c.trim() + '</span>'; }).join('') + '</div>';
                }
                return match;
            })
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    // ─── Crowd Data ──────────────────────────────────────────
    function loadCrowdData() {
        fetch(API + '/api/crowd/overview')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status === 'success') renderCrowd(data.data);
            })
            .catch(function () {});
    }

    function refreshCrowdData() {
        fetch(API + '/api/crowd/overview')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status === 'success') renderCrowd(data.data);
            });
    }

    function renderCrowd(overview) {
        var zones = overview.zones || {};
        var container = document.getElementById('zone-cards');
        if (!container) return;
        var html = '';

        Object.keys(zones).forEach(function (zid) {
            var z = zones[zid];
            var pct = z.percentage || 0;
            var level = z.level || 'low';

            html +=
                '<div class="zone-card" data-level="' + level + '">' +
                    '<div class="zone-top">' +
                        '<span class="zone-name">' + (z.name || 'Zone ' + zid) + '</span>' +
                        '<span class="zone-badge ' + level + '">' + level + '</span>' +
                    '</div>' +
                    '<div class="zone-bar"><div class="zone-fill ' + level + '" style="width:' + pct + '%"></div></div>' +
                    '<div class="zone-stats">' +
                        '<span>' + (z.occupancy || 0).toLocaleString() + ' / ' + (z.capacity || 0).toLocaleString() + '</span>' +
                        '<span>' + pct + '%</span>' +
                    '</div>' +
                '</div>';
        });

        container.innerHTML = html;

        Object.keys(zones).forEach(function (zid) {
            var z = zones[zid];
            var el = document.getElementById('zone-' + zid.toLowerCase() + '-svg');
            if (el) {
                var fillColors = { low: '#10b981', moderate: '#f59e0b', high: '#f97316', critical: '#ef4444', overflow: '#dc2626' };
                el.setAttribute('fill', fillColors[z.level] || '#3b82f6');
                el.style.opacity = 0.3 + (z.percentage / 100) * 0.7;
            }
        });
    }

    // ─── Transport ───────────────────────────────────────────
    function loadTransportData() {
        var el = document.getElementById('transport-list');
        if (!el) return;
        el.innerHTML =
            '<div class="info-card"><h4><i class="fas fa-parking"></i> Parking</h4>' +
            '<div class="info-row"><span>Lot A (North)</span><span>$40</span><span class="badge badge-green">EV Charging</span></div>' +
            '<div class="info-row"><span>Lot B (East)</span><span>$35</span><span class="badge badge-red">No EV</span></div>' +
            '<div class="info-row"><span>Lot C (South)</span><span>$38</span><span class="badge badge-green">EV Charging</span></div>' +
            '</div>' +
            '<div class="info-card"><h4><i class="fas fa-train"></i> Public Transit</h4>' +
            '<div class="info-row"><span>MetLife Station</span><span>0.5 km</span><span>Every 10 min</span></div>' +
            '<div class="info-row"><span>Bus Terminal</span><span>1.2 km</span><span>Every 15 min</span></div>' +
            '</div>' +
            '<div class="info-card"><h4><i class="fas fa-car"></i> Rideshare</h4>' +
            '<div class="info-row"><span>Pickup Zone</span><span>West Zone</span></div>' +
            '<div class="info-row"><span>Drop-off</span><span>North Zone</span></div>' +
            '</div>';
    }

    // ─── Eco ─────────────────────────────────────────────────
    function loadEcoData() {
        var el = document.getElementById('eco-list');
        if (!el) return;
        el.innerHTML =
            '<div class="eco-highlight"><div><h4>Eco Station North</h4><p style="font-size:.7rem;color:var(--text-3)">Plastic, Paper, Glass</p></div><span class="eco-pts">+50 pts</span></div>' +
            '<div class="eco-highlight"><div><h4>Eco Station East</h4><p style="font-size:.7rem;color:var(--text-3)">Plastic, Paper</p></div><span class="eco-pts">+30 pts</span></div>' +
            '<div class="eco-highlight"><div><h4>Eco Station South</h4><p style="font-size:.7rem;color:var(--text-3)">All + Food Waste</p></div><span class="eco-pts">+75 pts</span></div>' +
            '<div class="info-card"><h4><i class="fas fa-leaf"></i> Green Tips</h4>' +
            '<div class="info-row"><span>Bike to stadium</span><span class="badge badge-green">+200 pts</span></div>' +
            '<div class="info-row"><span>Public transit</span><span class="badge badge-green">+100 pts</span></div>' +
            '<div class="info-row"><span>Reusable container</span><span class="badge badge-green">+75 pts</span></div>' +
            '</div>';
    }

    // ─── Facility Map ────────────────────────────────────────
    function loadFacilityMap() {
        var facilities = [
            { icon: 'fa-door-open', name: 'Gate E1 \u2014 Main North', accessible: true },
            { icon: 'fa-door-open', name: 'Gate E2 \u2014 East', accessible: true },
            { icon: 'fa-door-open', name: 'Gate E3 \u2014 South', accessible: true },
            { icon: 'fa-door-open', name: 'Gate E4 \u2014 VIP', accessible: true },
            { icon: 'fa-restroom', name: 'Restroom North', accessible: true },
            { icon: 'fa-restroom', name: 'Restroom East', accessible: true },
            { icon: 'fa-utensils', name: 'Food Court North', extra: 'American, Mexican' },
            { icon: 'fa-utensils', name: 'Food Court East', extra: 'Asian, Italian' },
            { icon: 'fa-utensils', name: 'Food Court South', extra: 'Halal, Vegan' },
            { icon: 'fa-utensils', name: 'Food Court West', extra: 'Burgers, Pizza' },
            { icon: 'fa-medkit', name: 'Medical Station North' },
            { icon: 'fa-medkit', name: 'Medical Station South' },
            { icon: 'fa-recycle', name: 'Eco Station North' },
            { icon: 'fa-recycle', name: 'Eco Station South' }
        ];

        var el = document.getElementById('facility-list');
        if (!el) return;
        var html = '';
        facilities.forEach(function (f) {
            var badge = f.accessible ? '<span class="badge badge-green">Accessible</span>' : '';
            var extra = f.extra ? '<div class="facility-sub">' + f.extra + '</div>' : '';
            html +=
                '<div class="facility-item">' +
                    '<div class="facility-icon"><i class="fas ' + f.icon + '"></i></div>' +
                    '<div class="facility-info"><div class="facility-name">' + f.name + '</div>' + extra + '</div>' +
                    badge +
                '</div>';
        });
        el.innerHTML = html;
    }

    // ─── Command Center ──────────────────────────────────────
    function loadCommandCenter() {
        loadKPIs();
        loadRiskGrid();
        loadAlerts();
        loadStaffGrid();
        loadAIInsights();
        loadCharts();
    }

    function loadKPIs() {
        fetch(API + '/api/dashboard/kpis')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') return;
                var container = document.getElementById('kpi-grid');
                if (!container) return;
                var kpis = data.data;
                var icons = ['fa-users', 'fa-door-open', 'fa-clock', 'fa-shield-alt', 'fa-leaf', 'fa-exclamation-circle'];
                var html = '';
                var i = 0;
                Object.keys(kpis).forEach(function (key) {
                    var kpi = kpis[key];
                    var label = key.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                    html +=
                        '<div class="kpi">' +
                            '<div class="kpi-label"><i class="fas ' + (icons[i] || 'fa-chart-line') + '"></i> ' + label + '</div>' +
                            '<div class="kpi-val" style="color:var(--text)">' + kpi.value + '<span style="font-size:.6rem;color:var(--text-3)">' + kpi.unit + '</span></div>' +
                            '<div class="kpi-sub">Target: ' + kpi.target + kpi.unit + ' \u00b7 ' + kpi.trend + '</div>' +
                        '</div>';
                    i++;
                });
                container.innerHTML = html;
            });
    }

    function loadRiskGrid() {
        fetch(API + '/api/analytics/risks')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') return;
                var html = '';
                Object.keys(data.data).forEach(function (zid) {
                    var r = data.data[zid];
                    var color = r.risk_level === 'critical' ? 'var(--red)' : r.risk_level === 'high' ? 'var(--amber)' : r.risk_level === 'moderate' ? 'var(--blue)' : 'var(--green)';
                    html +=
                        '<div class="risk-box">' +
                            '<div class="risk-zone">Zone ' + zid + '</div>' +
                            '<div class="risk-val" style="color:' + color + '">' + r.risk_score + '%</div>' +
                            '<div class="risk-lbl" style="color:' + color + '">' + r.risk_level + '</div>' +
                        '</div>';
                });
                document.getElementById('risk-grid').innerHTML = html;
            });
    }

    function loadAlerts() {
        var alerts = [
            { type: 'warning', icon: 'fa-exclamation-triangle', text: 'Zone C approaching 80% capacity', time: '2 min ago' },
            { type: 'success', icon: 'fa-check-circle', text: 'Halftime rush managed successfully', time: '5 min ago' },
            { type: 'info', icon: 'fa-info-circle', text: 'New eco station activated in Zone D', time: '8 min ago' },
            { type: 'danger', icon: 'fa-bell', text: 'High noise levels detected in Zone A', time: '12 min ago' },
            { type: 'success', icon: 'fa-check-circle', text: 'Medical response time: 2.1 min average', time: '15 min ago' }
        ];
        var html = '';
        alerts.forEach(function (a) {
            html +=
                '<div class="alert-row ' + a.type + '">' +
                    '<i class="fas ' + a.icon + ' alert-icon"></i>' +
                    '<div><div class="alert-text">' + a.text + '</div><div class="alert-time">' + a.time + '</div></div>' +
                '</div>';
        });
        document.getElementById('alerts-feed').innerHTML = html;
    }

    function loadStaffGrid() {
        fetch(API + '/api/dashboard/staff')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') return;
                var depts = data.data.departments;
                var html = '';
                Object.keys(depts).forEach(function (key) {
                    var d = depts[key];
                    var pct = Math.round(d.deployed / d.total * 100);
                    var label = key.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                    html +=
                        '<div class="staff-row">' +
                            '<span class="staff-dept">' + label + '</span>' +
                            '<div class="staff-bar"><div class="staff-fill" style="width:' + pct + '%"></div></div>' +
                            '<span class="staff-ct">' + d.deployed + '/' + d.total + '</span>' +
                        '</div>';
                });
                document.getElementById('staff-grid').innerHTML = html;
            });
    }

    function loadAIInsights() {
        fetch(API + '/api/analytics/insights')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') return;
                var suggestions = data.data.optimization_suggestions || [];
                var html = '';
                suggestions.forEach(function (s) {
                    html +=
                        '<div class="ai-item">' +
                            '<div class="ai-type"><i class="fas fa-brain"></i> AI Recommendation</div>' +
                            '<div class="ai-text">' + s + '</div>' +
                        '</div>';
                });
                document.getElementById('ai-insights').innerHTML = html;
            });
    }

    function loadCharts() {
        fetch(API + '/api/crowd/heatmap')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') return;
                var ctx = document.getElementById('chart-crowd');
                if (!ctx) return;

                var zones = {};
                data.data.forEach(function (d) {
                    if (!zones[d.zone]) zones[d.zone] = [];
                    zones[d.zone].push(d.density);
                });

                var labels = Object.keys(zones['A'] || {}).map(function (_, i) { return 'S' + (i + 1); });
                var chartColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
                var datasets = Object.keys(zones).map(function (z, i) {
                    return {
                        label: 'Zone ' + z,
                        data: zones[z],
                        borderColor: chartColors[i],
                        backgroundColor: chartColors[i] + '20',
                        fill: true, tension: 0.4, borderWidth: 2
                    };
                });

                if (crowdChart) crowdChart.destroy();
                crowdChart = new Chart(ctx, {
                    type: 'line',
                    data: { labels: labels, datasets: datasets },
                    options: {
                        responsive: true,
                        plugins: { legend: { labels: { color: '#94a3c8', font: { size: 10 } } } },
                        scales: {
                            x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
                            y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.04)' }, min: 0, max: 100 }
                        }
                    }
                });
            });

        fetch(API + '/api/sentiment/chart')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var ctx = document.getElementById('chart-sentiment');
                if (!ctx) return;
                var chartData = data.data || [];
                var labels = chartData.map(function (_, i) { return '' + (i + 1); });
                var scores = chartData.map(function (d) { return d.score || 5; });

                if (sentimentChart) sentimentChart.destroy();
                sentimentChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Satisfaction',
                            data: scores,
                            backgroundColor: scores.map(function (s) {
                                return s >= 7 ? '#10b981' : s >= 5 ? '#f59e0b' : '#ef4444';
                            }),
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { display: false } },
                            y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.04)' }, min: 0, max: 10 }
                        }
                    }
                });
            });
    }

})();
