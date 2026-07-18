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
            // Facility names
            fac_gate1: 'Gate E1 \u2014 Main North', fac_gate2: 'Gate E2 \u2014 East', fac_gate3: 'Gate E3 \u2014 South', fac_gate4: 'Gate E4 \u2014 VIP',
            fac_rest_n: 'Restroom North', fac_rest_e: 'Restroom East',
            fac_food_n: 'Food Court North', fac_food_e: 'Food Court East', fac_food_s: 'Food Court South', fac_food_w: 'Food Court West',
            fac_food_n_sub: 'American, Mexican', fac_food_e_sub: 'Asian, Italian', fac_food_s_sub: 'Halal, Vegan', fac_food_w_sub: 'Burgers, Pizza',
            fac_med_n: 'Medical Station North', fac_med_s: 'Medical Station South',
            fac_eco_n: 'Eco Station North', fac_eco_s: 'Eco Station South',
            fac_accessible: 'Accessible',
            // Transport
            tr_parking: 'Parking', tr_lot_a: 'Lot A (North)', tr_lot_b: 'Lot B (East)', tr_lot_c: 'Lot C (South)',
            tr_ev: 'EV Charging', tr_no_ev: 'No EV',
            tr_transit: 'Public Transit', tr_metlife: 'MetLife Station', tr_bus: 'Bus Terminal',
            tr_every: 'Every', tr_min: 'min',
            tr_rideshare: 'Rideshare', tr_pickup: 'Pickup Zone', tr_dropoff: 'Drop-off',
            tr_west: 'West Zone', tr_north: 'North Zone',
            // Eco
            eco_station_n: 'Eco Station North', eco_station_e: 'Eco Station East', eco_station_s: 'Eco Station South',
            eco_materials_1: 'Plastic, Paper, Glass', eco_materials_2: 'Plastic, Paper', eco_materials_3: 'All + Food Waste',
            eco_tips: 'Green Tips', eco_bike: 'Bike to stadium', eco_transit: 'Public transit', eco_reusable: 'Reusable container',
            eco_pts: 'pts',
            // Alerts
            alert_1: 'Zone C approaching 80% capacity', alert_1_time: '2 min ago',
            alert_2: 'Halftime rush managed successfully', alert_2_time: '5 min ago',
            alert_3: 'New eco station activated in Zone D', alert_3_time: '8 min ago',
            alert_4: 'High noise levels detected in Zone A', alert_4_time: '12 min ago',
            alert_5: 'Medical response time: 2.1 min average', alert_5_time: '15 min ago',
            // Staff
            staff_cleaning: 'Cleaning', staff_crowd: 'Crowd Mgmt', staff_guest: 'Guest Services', staff_medical: 'Medical', staff_security: 'Security',
            // AI
            ai_recommendation: 'AI Recommendation',
            // Zones
            zone_a: 'North Stand', zone_b: 'East Stand', zone_c: 'South Stand', zone_d: 'West Stand',
            level_low: 'low', level_moderate: 'moderate', level_high: 'high', level_critical: 'critical', level_overflow: 'overflow',
            svg_a: 'ZONE A \u2014 NORTH', svg_b: 'ZONE B \u2014 EAST', svg_c: 'ZONE C \u2014 SOUTH', svg_d: 'ZONE D \u2014 WEST',
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
            fac_gate1: 'Puerta E1 \u2014 Norte Principal', fac_gate2: 'Puerta E2 \u2014 Este', fac_gate3: 'Puerta E3 \u2014 Sur', fac_gate4: 'Puerta E4 \u2014 VIP',
            fac_rest_n: 'Ba\u00f1o Norte', fac_rest_e: 'Ba\u00f1o Este',
            fac_food_n: 'Comedor Norte', fac_food_e: 'Comedor Este', fac_food_s: 'Comedor Sur', fac_food_w: 'Comedor Oeste',
            fac_food_n_sub: 'Americano, Mexicano', fac_food_e_sub: 'Asi\u00e1tico, Italiano', fac_food_s_sub: 'Halal, Vegano', fac_food_w_sub: 'Hamburguesas, Pizza',
            fac_med_n: 'Estaci\u00f3n M\u00e9dica Norte', fac_med_s: 'Estaci\u00f3n M\u00e9dica Sur',
            fac_eco_n: 'Estaci\u00f3n Eco Norte', fac_eco_s: 'Estaci\u00f3n Eco Sur', fac_accessible: 'Accesible',
            tr_parking: 'Estacionamiento', tr_lot_a: 'Lote A (Norte)', tr_lot_b: 'Lote B (Este)', tr_lot_c: 'Lote C (Sur)',
            tr_ev: 'Carga EV', tr_no_ev: 'Sin EV', tr_transit: 'Transporte P\u00fablico', tr_metlife: 'Estaci\u00f3n MetLife', tr_bus: 'Terminal de Bus',
            tr_every: 'Cada', tr_min: 'min', tr_rideshare: 'Viaje Compartido', tr_pickup: 'Zona de Recogida', tr_dropoff: 'Bajada',
            tr_west: 'Zona Oeste', tr_north: 'Zona Norte',
            eco_station_n: 'Estaci\u00f3n Eco Norte', eco_station_e: 'Estaci\u00f3n Eco Este', eco_station_s: 'Estaci\u00f3n Eco Sur',
            eco_materials_1: 'Pl\u00e1stico, Papel, Vidrio', eco_materials_2: 'Pl\u00e1stico, Papel', eco_materials_3: 'Todo + Residuos de Comida',
            eco_tips: 'Consejos Verdes', eco_bike: 'Ir en bici al estadio', eco_transit: 'Transporte p\u00fablico', eco_reusable: 'Contenedor reutilizable', eco_pts: 'pts',
            alert_1: 'Zona C al 80% de capacidad', alert_1_time: 'hace 2 min',
            alert_2: 'Rush de medio tiempo gestionado', alert_2_time: 'hace 5 min',
            alert_3: 'Nueva estaci\u00f3n eco activada en Zona D', alert_3_time: 'hace 8 min',
            alert_4: 'Altos niveles de ruido en Zona A', alert_4_time: 'hace 12 min',
            alert_5: 'Tiempo m\u00e9dico: 2.1 min promedio', alert_5_time: 'hace 15 min',
            staff_cleaning: 'Limpieza', staff_crowd: 'Gesti\u00f3n Multitud', staff_guest: 'Servicios al Cliente', staff_medical: 'M\u00e9dico', staff_security: 'Seguridad',
            ai_recommendation: 'Recomendaci\u00f3n IA',
            zone_a: 'Tribuna Norte', zone_b: 'Tribuna Este', zone_c: 'Tribuna Sur', zone_d: 'Tribuna Oeste',
            level_low: 'bajo', level_moderate: 'moderado', level_high: 'alto', level_critical: 'cr\u00edtico', level_overflow: 'desbordado',
            svg_a: 'ZONA A \u2014 NORTE', svg_b: 'ZONA B \u2014 ESTE', svg_c: 'ZONA C \u2014 SUR', svg_d: 'ZONA D \u2014 OESTE',
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
            fac_gate1: 'Porte E1 \u2014 Nord Principal', fac_gate2: 'Porte E2 \u2014 Est', fac_gate3: 'Porte E3 \u2014 Sud', fac_gate4: 'Porte E4 \u2014 VIP',
            fac_rest_n: 'Toilettes Nord', fac_rest_e: 'Toilettes Est',
            fac_food_n: 'Food Court Nord', fac_food_e: 'Food Court Est', fac_food_s: 'Food Court Sud', fac_food_w: 'Food Court Ouest',
            fac_food_n_sub: 'Am\u00e9ricain, Mexicain', fac_food_e_sub: 'Asiatique, Italien', fac_food_s_sub: 'Halal, V\u00e9g\u00e9tal', fac_food_w_sub: 'Burgers, Pizza',
            fac_med_n: 'Poste M\u00e9dical Nord', fac_med_s: 'Poste M\u00e9dical Sud',
            fac_eco_n: 'Station \u00c9co Nord', fac_eco_s: 'Station \u00c9co Sud', fac_accessible: 'Accessible',
            tr_parking: 'Parking', tr_lot_a: 'Zone A (Nord)', tr_lot_b: 'Zone B (Est)', tr_lot_c: 'Zone C (Sud)',
            tr_ev: 'Recharge EV', tr_no_ev: 'Pas de EV', tr_transit: 'Transport en Commun', tr_metlife: 'Station MetLife', tr_bus: 'Gare Routi\u00e8re',
            tr_every: 'Tous les', tr_min: 'min', tr_rideshare: 'Covoiturage', tr_pickup: 'Zone de Prise', tr_dropoff: 'D\u00e9pose',
            tr_west: 'Zone Ouest', tr_north: 'Zone Nord',
            eco_station_n: 'Station \u00c9co Nord', eco_station_e: 'Station \u00c9co Est', eco_station_s: 'Station \u00c9co Sud',
            eco_materials_1: 'Plastique, Papier, Verre', eco_materials_2: 'Plastique, Papier', eco_materials_3: 'Tout + D\u00e9chets Alimentaires',
            eco_tips: 'Conseils \u00c9co', eco_bike: 'V\u00e9lo au stade', eco_transit: 'Transport en commun', eco_reusable: 'Conteneur r\u00e9utilisable', eco_pts: 'pts',
            alert_1: 'Zone C \u00e0 80% de capacit\u00e9', alert_1_time: 'il y a 2 min',
            alert_2: 'Rush de la mi-temps g\u00e9r\u00e9', alert_2_time: 'il y a 5 min',
            alert_3: 'Nouvelle station \u00c9co activ\u00e9e Zone D', alert_3_time: 'il y a 8 min',
            alert_4: 'Niveaux de bruit \u00e9lev\u00e9s Zone A', alert_4_time: 'il y a 12 min',
            alert_5: 'Temps m\u00e9dical: 2.1 min en moyenne', alert_5_time: 'il y a 15 min',
            staff_cleaning: 'Nettoyage', staff_crowd: 'Gestion Foule', staff_guest: 'Services Client', staff_medical: 'M\u00e9dical', staff_security: 'S\u00e9curit\u00e9',
            ai_recommendation: 'Recommandation IA',
            zone_a: 'Tribune Nord', zone_b: 'Tribune Est', zone_c: 'Tribune Sud', zone_d: 'Tribune Ouest',
            level_low: 'faible', level_moderate: 'mod\u00e9r\u00e9', level_high: '\u00e9lev\u00e9', level_critical: 'critique', level_overflow: 'd\u00e9bordement',
            svg_a: 'TRIBUNE A \u2014 NORD', svg_b: 'TRIBUNE B \u2014 EST', svg_c: 'TRIBUNE C \u2014 SUD', svg_d: 'TRIBUNE D \u2014 OUEST',
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
            fac_gate1: 'Tor E1 \u2014 Haupt Nord', fac_gate2: 'Tor E2 \u2014 Ost', fac_gate3: 'Tor E3 \u2014 S\u00fcd', fac_gate4: 'Tor E4 \u2014 VIP',
            fac_rest_n: 'Toilette Nord', fac_rest_e: 'Toilette Ost',
            fac_food_n: 'Essenscourt Nord', fac_food_e: 'Essenscourt Ost', fac_food_s: 'Essenscourt S\u00fcd', fac_food_w: 'Essenscourt West',
            fac_food_n_sub: 'Amerikanisch, Mexikanisch', fac_food_e_sub: 'Asiatisch, Italienisch', fac_food_s_sub: 'Halal, Vegan', fac_food_w_sub: 'Burgers, Pizza',
            fac_med_n: 'Medizinische Station Nord', fac_med_s: 'Medizinische Station S\u00fcd',
            fac_eco_n: '\u00d6ko-Station Nord', fac_eco_s: '\u00d6ko-Station S\u00fcd', fac_accessible: 'Barrierefrei',
            tr_parking: 'Parkplatz', tr_lot_a: 'Lot A (Nord)', tr_lot_b: 'Lot B (Ost)', tr_lot_c: 'Lot C (S\u00fcd)',
            tr_ev: 'EV-Laden', tr_no_ev: 'Kein EV', tr_transit: '\u00d6ffentlicher Verkehr', tr_metlife: 'MetLife Station', tr_bus: 'Busbahnhof',
            tr_every: 'Alle', tr_min: 'Min', tr_rideshare: 'Fahrgemeinschaft', tr_pickup: 'Abholzone', tr_dropoff: 'Absprung',
            tr_west: 'Westzone', tr_north: 'Nordzone',
            eco_station_n: '\u00d6ko-Station Nord', eco_station_e: '\u00d6ko-Station Ost', eco_station_s: '\u00d6ko-Station S\u00fcd',
            eco_materials_1: 'Kunststoff, Papier, Glas', eco_materials_2: 'Kunststoff, Papier', eco_materials_3: 'Alles + Lebensmittelabf\u00e4lle',
            eco_tips: 'Umwelttipps', eco_bike: 'Mit dem Rad zum Stadion', eco_transit: '\u00d6ffentlicher Verkehr', eco_reusable: 'Wiederverwendbarer Beh\u00e4lter', eco_pts: 'Pkte',
            alert_1: 'Zone C n\u00e4hert sich 80% Kapazit\u00e4t', alert_1_time: 'vor 2 Min',
            alert_2: 'Halftime-Rush erfolgreich', alert_2_time: 'vor 5 Min',
            alert_3: 'Neue \u00d6ko-Station in Zone D', alert_3_time: 'vor 8 Min',
            alert_4: 'Hohe Ger\u00e4uschpegel in Zone A', alert_4_time: 'vor 12 Min',
            alert_5: 'Med. Reaktionszeit: 2.1 Min', alert_5_time: 'vor 15 Min',
            staff_cleaning: 'Reinigung', staff_crowd: 'Mengenverwaltung', staff_guest: 'G\u00e4steservice', staff_medical: 'Medizin', staff_security: 'Sicherheit',
            ai_recommendation: 'KI-Empfehlung',
            zone_a: 'Nordtribüne', zone_b: 'Osttribüne', zone_c: 'Südtribüne', zone_d: 'Westtribüne',
            level_low: 'niedrig', level_moderate: 'mittel', level_high: 'hoch', level_critical: 'kritisch', level_overflow: 'überlauf',
            svg_a: 'ZONE A \u2014 NORD', svg_b: 'ZONE B \u2014 OST', svg_c: 'ZONE C \u2014 S\u00dcD', svg_d: 'ZONE D \u2014 WEST',
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
            fac_gate1: 'E1\u53f7\u95e8 \u2014 \u5317\u4fa7\u4e3b\u5165\u53e3', fac_gate2: 'E2\u53f7\u95e8 \u2014 \u4e1c\u4fa7', fac_gate3: 'E3\u53f7\u95e8 \u2014 \u5357\u4fa7', fac_gate4: 'E4\u53f7\u95e8 \u2014 VIP',
            fac_rest_n: '\u5317\u4fa7\u6d17\u624b\u95f4', fac_rest_e: '\u4e1c\u4fa7\u6d17\u624b\u95f4',
            fac_food_n: '\u5317\u4fa7\u7f8e\u98df\u5e02\u573a', fac_food_e: '\u4e1c\u4fa7\u7f8e\u98df\u5e02\u573a', fac_food_s: '\u5357\u4fa7\u7f8e\u98df\u5e02\u573a', fac_food_w: '\u897f\u4fa7\u7f8e\u98df\u5e02\u573a',
            fac_food_n_sub: '\u7f8e\u56fd\u3001\u58a8\u897f\u54e5', fac_food_e_sub: '\u4e9a\u6d32\u3001\u610f\u5927\u5229', fac_food_s_sub: '\u6e05\u771f\u3001\u7d20\u98df', fac_food_w_sub: '\u6c49\u5821\u3001\u62b9\u8336',
            fac_med_n: '\u5317\u4fa7\u533b\u7597\u7ad9', fac_med_s: '\u5357\u4fa7\u533b\u7597\u7ad9',
            fac_eco_n: '\u5317\u4fa7\u73af\u4fdd\u7ad9', fac_eco_s: '\u5357\u4fa7\u73af\u4fdd\u7ad9', fac_accessible: '\u65e0\u969c\u788d',
            tr_parking: '\u505c\u8f66\u573a', tr_lot_a: 'A\u533a\uff08\u5317\uff09', tr_lot_b: 'B\u533a\uff08\u4e1c\uff09', tr_lot_c: 'C\u533a\uff08\u5357\uff09',
            tr_ev: '\u7535\u52a8\u5145\u7535', tr_no_ev: '\u65e0\u5145\u7535', tr_transit: '\u516c\u5171\u4ea4\u901a', tr_metlife: 'MetLife\u7ad9', tr_bus: '\u516c\u4ea4\u7ad9',
            tr_every: '\u6bcf', tr_min: '\u5206\u949f', tr_rideshare: '\u62ff\u62ff\u8f66', tr_pickup: '\u4e0a\u8f66\u70b9', tr_dropoff: '\u4e0b\u8f66\u70b9',
            tr_west: '\u897f\u533a', tr_north: '\u5317\u533a',
            eco_station_n: '\u5317\u4fa7\u73af\u4fdd\u7ad9', eco_station_e: '\u4e1c\u4fa7\u73af\u4fdd\u7ad9', eco_station_s: '\u5357\u4fa7\u73af\u4fdd\u7ad9',
            eco_materials_1: '\u5851\u6599\u3001\u7eb8\u5f20\u3001\u73bb\u7483', eco_materials_2: '\u5851\u6599\u3001\u7eb8\u5f20', eco_materials_3: '\u5168\u90e8 + \u996e\u98df\u5783\u573e',
            eco_tips: '\u7eff\u8272\u5c0f\u8d34\u58eb', eco_bike: '\u9a91\u8f66\u5230\u4f53\u80b2\u573a', eco_transit: '\u516c\u5171\u4ea4\u901a', eco_reusable: '\u53ef\u91cd\u590d\u4f7f\u7528\u5bb9\u5668', eco_pts: '\u5206',
            alert_1: 'C\u533a\u63a5\u8fd180%\u5bb9\u91cf', alert_1_time: '2\u5206\u949f\u524d',
            alert_2: '\u4e2d\u573a\u4f11\u606f\u9ad8\u5cf0\u5df2\u5904\u7406', alert_2_time: '5\u5206\u949f\u524d',
            alert_3: '\u65b0\u73af\u4fdd\u7ad9\u5df2\u5728D\u533a\u542f\u7528', alert_3_time: '8\u5206\u949f\u524d',
            alert_4: 'A\u533a\u68c0\u6d4b\u5230\u9ad8\u566a\u97f3', alert_4_time: '12\u5206\u949f\u524d',
            alert_5: '\u533b\u7597\u54cd\u5e94\u65f6\u95f4: \u5e73\u57472.1\u5206\u949f', alert_5_time: '15\u5206\u949f\u524d',
            staff_cleaning: '\u6e05\u6d01', staff_crowd: '\u4eba\u7fa4\u7ba1\u7406', staff_guest: '\u5ba2\u6237\u670d\u52a1', staff_medical: '\u533b\u7597', staff_security: '\u5b89\u4fdd',
            ai_recommendation: 'AI\u5efa\u8bae',
            zone_a: '\u5317\u770b\u53f0', zone_b: '\u4e1c\u770b\u53f0', zone_c: '\u5357\u770b\u53f0', zone_d: '\u897f\u770b\u53f0',
            level_low: '\u4f4e', level_moderate: '\u4e2d', level_high: '\u9ad8', level_critical: '\u4e25\u91cd', level_overflow: '\u6ea2\u51fa',
            svg_a: '\u533a\u57df A \u2014 \u5317', svg_b: '\u533a\u57df B \u2014 \u4e1c', svg_c: '\u533a\u57df C \u2014 \u5357', svg_d: '\u533a\u57df D \u2014 \u897f',
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
            fac_gate1: '\u30b8\u30fc\u30c8E1 \u2014 \u5317\u5074\u30e1\u30a4\u30f3', fac_gate2: '\u30b8\u30fc\u30c8E2 \u2014 \u6771\u5074', fac_gate3: '\u30b8\u30fc\u30c8E3 \u2014 \u5357\u5074', fac_gate4: '\u30b8\u30fc\u30c8E4 \u2014 VIP',
            fac_rest_n: '\u5317\u5074\u30c8\u30a4\u30ec', fac_rest_e: '\u6771\u5074\u30c8\u30a4\u30ec',
            fac_food_n: '\u5317\u5074\u30d5\u30fc\u30c9\u30b3\u30fc\u30c8', fac_food_e: '\u6771\u5074\u30d5\u30fc\u30c9\u30b3\u30fc\u30c8', fac_food_s: '\u5357\u5074\u30d5\u30fc\u30c9\u30b3\u30fc\u30c8', fac_food_w: '\u897f\u5074\u30d5\u30fc\u30c9\u30b3\u30fc\u30c8',
            fac_food_n_sub: '\u30a2\u30e1\u30ea\u30ab\u3001\u30e1\u30ad\u30b7\u30b3', fac_food_e_sub: '\u30a2\u30b8\u30a2\u3001\u30a4\u30bf\u30ea\u30a2\u30f3', fac_food_s_sub: '\u30cf\u30e9\u30fc\u3001\u30d9\u30b8\u30bf\u30eb', fac_food_w_sub: '\u30d0\u30fc\u30ac\u30fc\u3001\u30d4\u30b6',
            fac_med_n: '\u5317\u5074\u533b\u7642\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3', fac_med_s: '\u5357\u5074\u533b\u7642\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3',
            fac_eco_n: '\u5317\u5074\u30a8\u30b3\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3', fac_eco_s: '\u5357\u5074\u30a8\u30b3\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3', fac_accessible: '\u30a2\u30af\u30bb\u30b7\u30d3\u30eb',
            tr_parking: '\u99d0\u8eeb\u5834', tr_lot_a: '\u30ed\u30c3\u30c8A\uff08\u5317\uff09', tr_lot_b: '\u30ed\u30c3\u30c8B\uff08\u6771\uff09', tr_lot_c: '\u30ed\u30c3\u30c8C\uff08\u5357\uff09',
            tr_ev: 'EV\u5145\u96fb', tr_no_ev: 'EV\u306a\u3057', tr_transit: '\u516c\u5171\u4ea4\u901a', tr_metlife: 'MetLife\u99c5', tr_bus: '\u30d0\u30b9\u30bf\u30fc\u30df\u30ca\u30eb',
            tr_every: '\u6bcf', tr_min: '\u5206', tr_rideshare: '\u30e9\u30a4\u30c9\u30b7\u30a7\u30a2', tr_pickup: '\u4e58\u308a\u5834', tr_dropoff: '\u964d\u8fbc\u307f',
            tr_west: '\u897f\u5074', tr_north: '\u5317\u5074',
            eco_station_n: '\u5317\u5074\u30a8\u30b3\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3', eco_station_e: '\u6771\u5074\u30a8\u30b3\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3', eco_station_s: '\u5357\u5074\u30a8\u30b3\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3',
            eco_materials_1: '\u30d7\u30e9\u30b9\u30c1\u30c3\u30af\u3001\u7d19\u3001\u30ac\u30e9\u30b9', eco_materials_2: '\u30d7\u30e9\u30b9\u30c1\u30c3\u30af\u3001\u7d19', eco_materials_3: '\u5168\u3066 + \u98df\u3079\u7269\u5ecf\u5831',
            eco_tips: '\u30a8\u30b3\u30c1\u30c3\u30d7', eco_bike: '\u30d0\u30a4\u30af\u3067\u30b9\u30bf\u30b8\u30a2\u3078', eco_transit: '\u516c\u5171\u4ea4\u901a', eco_reusable: '\u518d\u5229\u7528\u5bb9\u5668', eco_pts: '\u30dd\u30a4\u30f3\u30c8',
            alert_1: 'C\u30be\u30fc\u30f380%\u5bb9\u91cf\u8efd\u8d85', alert_1_time: '2\u5206\u524d',
            alert_2: '\u30cf\u30fc\u30bf\u30a4\u30e0\u30e9\u30b7\u30e5\u7ba1\u7406\u6e08\u307f', alert_2_time: '5\u5206\u524d',
            alert_3: '\u65b0\u30a8\u30b3\u30b9\u30c6\u30fc\u30b7\u30e7\u30f3D\u30be\u30fc\u30f3', alert_3_time: '8\u5206\u524d',
            alert_4: 'A\u30be\u30fc\u30f3\u9ad8\u97f3\u99f3\u691c\u51fa', alert_4_time: '12\u5206\u524d',
            alert_5: '\u533b\u7642\u5bfe\u5fdc\u6642\u9593: \u5e73\u57472.1\u5206', alert_5_time: '15\u5206\u524d',
            staff_cleaning: '\u6e05\u6b4a', staff_crowd: '\u4eba\u6ce2\u7ba1\u7406', staff_guest: '\u30ac\u30b9\u30c8\u30b5\u30fc\u30d3\u30b9', staff_medical: '\u533b\u7642', staff_security: '\u5b89\u5168',
            ai_recommendation: 'AI\u304a\u3059\u3059\u3081',
            zone_a: '\u5317\u30b9\u30bf\u30f3\u30c9', zone_b: '\u6771\u30b9\u30bf\u30f3\u30c9', zone_c: '\u5357\u30b9\u30bf\u30f3\u30c9', zone_d: '\u897f\u30b9\u30bf\u30f3\u30c9',
            level_low: '\u4f4e', level_moderate: '\u4e2d', level_high: '\u9ad8', level_critical: '\u5371\u967a', level_overflow: '\u30aa\u30fc\u30d0\u30fc\u30d5\u30ed\u30fc',
            svg_a: '\u30b8\u30e7\u30f3 A \u2014 \u5317', svg_b: '\u30b8\u30e7\u30f3 B \u2014 \u6771', svg_c: '\u30b8\u30e7\u30f3 C \u2014 \u5357', svg_d: '\u30b8\u30e7\u30f3 D \u2014 \u897f',
        },
        ko: {
            loader_sub: 'AI 시스템 초기화',
            nav_fan: '팬 경험', nav_cmd: '지휘 센터',
            systems_online: '시스템 온라인',
            hero_badge: 'FIFA 월드컵 2026',
            hero_title_1: '나만의', hero_title_2: 'AI 경기장', hero_title_3: '어시스턴트',
            hero_sub: '더 똑똑하게 내비게이션하세요. Google Gemini 2.5 Flash로 구동됩니다.',
            stat_capacity: '수용량', stat_endpoints: 'API 엔드포인트', stat_languages: '언어', stat_tests: '테스트',
            ai_assistant: 'AI 어시스턴트', ai_sub: 'Gemini 2.5 Flash 기술', active: '활성',
            greeting_title: 'StadiumIQ에 오신 것을 환영합니다!',
            greeting_sub: '<strong>FIFA 월드컵 2026</strong> MetLife 경기장의 AI 어시스턴트입니다.',
            feat_nav: '내비게이션', feat_crowds: '혼잡도', feat_a11y: '접근성', feat_eco: '지속가능성', feat_match: '경기 정보', feat_transport: '교통',
            just_now: '방금',
            q_restroom: '화장실', q_food: '음식', q_crowds: '혼잡도', q_parking: '주차', q_accessible: '접근성', q_eco: '에코', q_schedule: '일정', q_medical: '의료',
            chat_placeholder: '경기장에 대해 무엇이든 물어보세요...',
            tab_crowd: '혼잡도', tab_map: '지도', tab_transport: '교통', tab_eco: '에코',
            crowd_title: '실시간 혼잡도', live: '실시간',
            map_title: '시설 안내도', transport_title: '교통 허브', eco_title: '지속가능성 대시보드',
            cmd_title: '운영 지휘 센터', cmd_sub: '실시간 경기장 인텔리전스 및 운영 분석',
            cmd_crowd: '인파 흐름', cmd_sentiment: '팬 감정', cmd_risk: '위험 평가',
            cmd_alerts: '실시간 알림', cmd_staff: '인력 배치', cmd_insights: 'AI 인사이트',
            footer_left: 'StadiumIQ v3.0 — Google Gemini 2.5 Flash로 구동',
            footer_right: 'FIFA 월드컵 2026 — MetLife 경기장',
            toast_ready: 'StadiumIQ 준비 완료! 무엇이든 물어보세요.',
            toast_lang: '언어가 변경되었습니다',
            fac_gate1: 'E1번 게이트 — 북쪽 메인', fac_gate2: 'E2번 게이트 — 동쪽', fac_gate3: 'E3번 게이트 — 남쪽', fac_gate4: 'E4번 게이트 — VIP',
            fac_rest_n: '북쪽 화장실', fac_rest_e: '동쪽 화장실',
            fac_food_n: '북쪽 푸드코트', fac_food_e: '동쪽 푸드코트', fac_food_s: '남쪽 푸드코트', fac_food_w: '서쪽 푸드코트',
            fac_food_n_sub: '미국식, 멕시코식', fac_food_e_sub: '아시안, 이탈리안', fac_food_s_sub: '할랄, 비건', fac_food_w_sub: '버거, 피자',
            fac_med_n: '북쪽 의료소', fac_med_s: '남쪽 의료소',
            fac_eco_n: '북쪽 에코스테이션', fac_eco_s: '남쪽 에코스테이션', fac_accessible: '접근성 지원',
            tr_parking: '주차장', tr_lot_a: 'A구역 (북쪽)', tr_lot_b: 'B구역 (동쪽)', tr_lot_c: 'C구역 (남쪽)',
            tr_ev: '전기차 충전', tr_no_ev: '충전 없음', tr_transit: '대중교통', tr_metlife: 'MetLife역', tr_bus: '버스 터미널',
            tr_every: '매', tr_min: '분', tr_rideshare: '카풀', tr_pickup: '승차장', tr_dropoff: '하차장',
            tr_west: '서쪽 구역', tr_north: '북쪽 구역',
            eco_station_n: '북쪽 에코스테이션', eco_station_e: '동쪽 에코스테이션', eco_station_s: '남쪽 에코스테이션',
            eco_materials_1: '플라스틱, 종이, 유리', eco_materials_2: '플라스틱, 종이', eco_materials_3: '전체 + 음식쓰레기',
            eco_tips: '그린 팁', eco_bike: '자전거로 경기장 가기', eco_transit: '대중교통 이용', eco_reusable: '재사용 용기', eco_pts: '점',
            alert_1: 'C구역 80% 수용량 접근', alert_1_time: '2분 전',
            alert_2: '하프타임 대응 성공', alert_2_time: '5분 전',
            alert_3: 'D구역 신규 에코스테이션 활성화', alert_3_time: '8분 전',
            alert_4: 'A구역 높은 소음 감지', alert_4_time: '12분 전',
            alert_5: '의료 대응시간: 평균 2.1분', alert_5_time: '15분 전',
            staff_cleaning: '청소', staff_crowd: '인파 관리', staff_guest: '고객 서비스', staff_medical: '의료', staff_security: '보안',
            ai_recommendation: 'AI 추천',
            zone_a: '북쪽 스탠드', zone_b: '동쪽 스탠드', zone_c: '남쪽 스탠드', zone_d: '서쪽 스탠드',
            level_low: '낮음', level_moderate: '보통', level_high: '높음', level_critical: '위험', level_overflow: '초과',
            svg_a: '존 A \u2014 북쪽', svg_b: '존 B \u2014 동쪽', svg_c: '존 C \u2014 남쪽', svg_d: '존 D \u2014 서쪽',
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
            fac_gate1: 'Port\u00e3o E1 \u2014 Norte Principal', fac_gate2: 'Port\u00e3o E2 \u2014 Leste', fac_gate3: 'Port\u00e3o E3 \u2014 Sul', fac_gate4: 'Port\u00e3o E4 \u2014 VIP',
            fac_rest_n: 'Banheiro Norte', fac_rest_e: 'Banheiro Leste',
            fac_food_n: 'Praça de Alimentação Norte', fac_food_e: 'Praça de Alimentação Leste', fac_food_s: 'Praça de Alimentação Sul', fac_food_w: 'Praça de Alimentação Oeste',
            fac_food_n_sub: 'Americano, Mexicano', fac_food_e_sub: 'Asiático, Italiano', fac_food_s_sub: 'Halal, Vegano', fac_food_w_sub: 'Hambúrgueres, Pizza',
            fac_med_n: 'Posto Médico Norte', fac_med_s: 'Posto Médico Sul',
            fac_eco_n: 'Posto Ecológico Norte', fac_eco_s: 'Posto Ecológico Sul', fac_accessible: 'Acessível',
            tr_parking: 'Estacionamento', tr_lot_a: 'Lote A (Norte)', tr_lot_b: 'Lote B (Leste)', tr_lot_c: 'Lote C (Sul)',
            tr_ev: 'Carregamento EV', tr_no_ev: 'Sem EV', tr_transit: 'Transporte Público', tr_metlife: 'Estação MetLife', tr_bus: 'Terminal de Ônibus',
            tr_every: 'A cada', tr_min: 'min', tr_rideshare: 'Boleia', tr_pickup: 'Zona de Embarque', tr_dropoff: 'Desembarque',
            tr_west: 'Zona Oeste', tr_north: 'Zona Norte',
            eco_station_n: 'Posto Ecológico Norte', eco_station_e: 'Posto Ecológico Leste', eco_station_s: 'Posto Ecológico Sul',
            eco_materials_1: 'Plástico, Papel, Vidro', eco_materials_2: 'Plástico, Papel', eco_materials_3: 'Tudo + Resíduos Alimentares',
            eco_tips: 'Dicas Verdes', eco_bike: 'Ir de bike ao estádio', eco_transit: 'Transporte público', eco_reusable: 'Recipiente reutilizável', eco_pts: 'pts',
            alert_1: 'Zona C a 80% da capacidade', alert_1_time: 'há 2 min',
            alert_2: 'Rush do intervalo gerenciado', alert_2_time: 'há 5 min',
            alert_3: 'Nova ecológica ativada na Zona D', alert_3_time: 'há 8 min',
            alert_4: 'Altos níveis de ruído na Zona A', alert_4_time: 'há 12 min',
            alert_5: 'Tempo médico: 2.1 min média', alert_5_time: 'há 15 min',
            staff_cleaning: 'Limpeza', staff_crowd: 'Gestão de Multidão', staff_guest: 'Serviços ao Cliente', staff_medical: 'Médico', staff_security: 'Segurança',
            ai_recommendation: 'Recomendação IA',
            zone_a: 'Arquibancada Norte', zone_b: 'Arquibancada Leste', zone_c: 'Arquibancada Sul', zone_d: 'Arquibancada Oeste',
            level_low: 'baixo', level_moderate: 'moderado', level_high: 'alto', level_critical: 'crítico', level_overflow: 'transbordamento',
            svg_a: 'ZONA A \u2014 NORTE', svg_b: 'ZONA B \u2014 LESTE', svg_c: 'ZONA C \u2014 SUL', svg_d: 'ZONA D \u2014 OESTE',
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
            fac_gate1: '\u0917\u0947\u091f E1 \u2014 \u092e\u0941\u0916\u094d\u092f \u0909\u0924\u094d\u0924\u0930', fac_gate2: '\u0917\u0947\u091f E2 \u2014 \u092a\u0942\u0930\u094d\u0935', fac_gate3: '\u0917\u0947\u091f E3 \u2014 \u0926\u0915\u094d\u0937\u093f\u0923', fac_gate4: '\u0917\u0947\u091f E4 \u2014 VIP',
            fac_rest_n: '\u0909\u0924\u094d\u0924\u0930 \u0936\u094c\u091a\u093e\u0918\u0930', fac_rest_e: '\u092a\u0942\u0930\u094d\u0935 \u0936\u094c\u091a\u093e\u0918\u0930',
            fac_food_n: '\u0909\u0924\u094d\u0924\u0930 \u092b\u0942\u0921 \u0915\u0949\u0930\u094d\u091f', fac_food_e: '\u092a\u0942\u0930\u094d\u0935 \u092b\u0942\u0921 \u0915\u0949\u0930\u094d\u091f', fac_food_s: '\u0926\u0915\u094d\u0937\u093f\u0923 \u092b\u0942\u0921 \u0915\u0949\u0930\u094d\u091f', fac_food_w: '\u092a\u0936\u094d\u091a\u093f\u092e \u092b\u0942\u0921 \u0915\u0949\u0930\u094d\u091f',
            fac_food_n_sub: '\u0905\u092e\u0947\u0930\u093f\u0915\u0940, \u092e\u0947\u0915\u094d\u0938\u093f\u0915\u0928', fac_food_e_sub: '\u090f\u0936\u093f\u092f\u093e\u0908, \u0907\u091f\u0932\u0940\u092f\u093e\u0908', fac_food_s_sub: '\u0939\u0932\u093e\u0932, \u0935\u0947\u0917\u0928', fac_food_w_sub: '\u092c\u0930\u094d\u0917\u0930, \u092a\u093f\u091c\u093c\u093e',
            fac_med_n: '\u0909\u0924\u094d\u0924\u0930 \u092e\u0947\u0921\u093f\u0915\u0932 \u0938\u094d\u091f\u0947\u0936\u0928', fac_med_s: '\u0926\u0915\u094d\u0937\u093f\u0923 \u092e\u0947\u0921\u093f\u0915\u0932 \u0938\u094d\u091f\u0947\u0936\u0928',
            fac_eco_n: '\u0909\u0924\u094d\u0924\u0930 \u091f\u093f\u0915\u093e \u0938\u094d\u091f\u0947\u0936\u0928', fac_eco_s: '\u0926\u0915\u094d\u0937\u093f\u0923 \u091f\u093f\u0915\u093e \u0938\u094d\u091f\u0947\u0936\u0928', fac_accessible: '\u0938\u0941\u0932\u092d',
            tr_parking: '\u092a\u093e\u0930\u094d\u0915\u093f\u0902\u0917', tr_lot_a: '\u0932\u0949\u091f A (\u0909\u0924\u094d\u0924\u0930)', tr_lot_b: '\u0932\u0949\u091f B (\u092a\u0942\u0930\u094d\u0935)', tr_lot_c: '\u0932\u0949\u091f C (\u0926\u0915\u094d\u0937\u093f\u0923)',
            tr_ev: 'EV \u091a\u093e\u0930\u094d\u091c', tr_no_ev: 'EV \u0928\u0939\u0940\u0902', tr_transit: '\u0938\u093e\u0930\u094d\u0935\u0939\u093f\u0915 \u092a\u0930\u093f\u0935\u0939\u093e\u0928', tr_metlife: 'MetLife \u0938\u094d\u091f\u0947\u0936\u0928', tr_bus: '\u092c\u0938 \u091f\u0930\u094d\u092e\u093f\u0928\u0932',
            tr_every: '\u0939\u0930', tr_min: '\u092e\u093f\u0928\u091f', tr_rideshare: '\u0915\u093e\u0930\u092a\u0942\u0932', tr_pickup: '\u0938\u094d\u0935\u0940\u0915\u093e\u0930\u0923 \u0915\u094d\u0937\u0947\u0924\u094d\u0930', tr_dropoff: '\u0909\u0924\u093e\u0930\u0923\u093e',
            tr_west: '\u092a\u0936\u094d\u091a\u093f\u092e \u0915\u094d\u0937\u0947\u0924\u094d\u0930', tr_north: '\u0909\u0924\u094d\u0924\u0930 \u0915\u094d\u0937\u0947\u0924\u094d\u0930',
            eco_station_n: '\u0909\u0924\u094d\u0924\u0930 \u091f\u093f\u0915\u093e \u0938\u094d\u091f\u0947\u0936\u0928', eco_station_e: '\u092a\u0942\u0930\u094d\u0935 \u091f\u093f\u0915\u093e \u0938\u094d\u091f\u0947\u0936\u0928', eco_station_s: '\u0926\u0915\u094d\u0937\u093f\u0923 \u091f\u093f\u0915\u093e \u0938\u094d\u091f\u0947\u0936\u0928',
            eco_materials_1: '\u092a\u094d\u0932\u093e\u0938\u094d\u091f\u093f\u0915, \u0915\u093e\u0917\u093c\u093e\u091c, \u0915\u093e\u0901\u091b', eco_materials_2: '\u092a\u094d\u0932\u093e\u0938\u094d\u091f\u093f\u0915, \u0915\u093e\u0917\u093c\u093e\u091c', eco_materials_3: '\u0938\u092c \u0915\u0941\u0937 \u0906\u0939\u093e\u0930 \u0938\u093e\u092e\u0917\u094d\u0930\u0940',
            eco_tips: '\u0939\u0930\u093e \u091f\u093f\u092a\u094d\u0938', eco_bike: '\u092c\u093e\u0907\u0915 \u0938\u0947 \u0938\u094d\u091f\u0947\u0921\u093f\u092f\u092e', eco_transit: '\u0938\u093e\u0930\u094d\u0935\u0939\u093f\u0915 \u092a\u0930\u093f\u0935\u0939\u093e\u0928', eco_reusable: '\u092a\u0941\u0928\u0930\u094d\u092f\u094b\u091c\u093f\u0924 \u0915\u0902\u091f\u0947\u0928\u0930', eco_pts: 'pts',
            alert_1: '\u091c\u094b\u0928 \u0938\u0940 80% \u0915\u094d\u0937\u092e\u0924\u093e \u0915\u0947 \u0915\u0930\u0940\u092c', alert_1_time: '2 \u092e\u093f\u0928 \u092a\u0939\u0932\u0947',
            alert_2: '\u0939\u093e\u092b\u091f\u093e\u0907\u092e \u0930\u0947\u0936 \u0938\u092b\u0932\u0924\u093e\u092a\u0942\u0930\u094d\u0935\u0915', alert_2_time: '5 \u092e\u093f\u0928 \u092a\u0939\u0932\u0947',
            alert_3: '\u091c\u094b\u0928 D \u092e\u0947\u0902 \u0928\u0908 \u091f\u093f\u0915\u093e \u0938\u094d\u091f\u0947\u0936\u0928 \u0938\u0915\u094d\u0930\u093f\u092f', alert_3_time: '8 \u092e\u093f\u0928 \u092a\u0939\u0932\u0947',
            alert_4: '\u091c\u094b\u0928 A \u092e\u0947\u0902 \u0909\u091a\u094d\u091a \u0936\u094b\u0930 \u0915\u093e \u092a\u0924\u093e', alert_4_time: '12 \u092e\u093f\u0928 \u092a\u0939\u0932\u0947',
            alert_5: '\u092e\u0947\u0921\u093f\u0915\u0932 \u092a\u094d\u0930\u0924\u093f\u0915\u094d\u0930\u093f\u092f\u093e: \u0914\u0938\u0924 \u0920 2.1', alert_5_time: '15 \u092e\u093f\u0928 \u092a\u0939\u0932\u0947',
            staff_cleaning: '\u0938\u092b\u093c\u093e\u0908', staff_crowd: '\u092d\u0940\u0921\u093c \u092a\u094d\u0930\u092c\u0902\u0927\u0928', staff_guest: '\u0917\u0948\u0938\u094d\u091f \u0938\u0947\u0935\u093e', staff_medical: '\u092e\u0947\u0921\u093f\u0915\u0932', staff_security: '\u0938\u0941\u0930\u0915\u094d\u0937\u093e',
            ai_recommendation: 'AI \u0938\u0941\u091a\u0928\u093e',
            zone_a: '\u0909\u0924\u094d\u0924\u0930 \u0938\u094d\u091f\u0948\u0902\u0921', zone_b: '\u092a\u0942\u0930\u094d\u0925 \u0938\u094d\u091f\u0948\u0902\u0921', zone_c: '\u0926\u0915\u094d\u0937\u093f\u0928 \u0938\u094d\u091f\u0948\u0902\u0921', zone_d: '\u092a\u0936\u094d\u091a\u093f\u092e \u0938\u094d\u091f\u0948\u0902\u0921',
            level_low: '\u0915\u092e', level_moderate: '\u092e\u0927\u094d\u092f\u092e', level_high: '\u0909\u091a\u094d\u091a', level_critical: '\u0917\u0902\u092D\u0940\u0930', level_overflow: '\u0905\u0924\u093f\u0930\u093f\u0915\u094d\u0924',
            svg_a: '\u091c\u094b\u0928 A \u2014 \u0909\u0924\u094d\u0924\u0930', svg_b: '\u091c\u094b\u0928 B \u2014 \u092a\u0942\u0930\u094d\u0925', svg_c: '\u091c\u094b\u0928 C \u2014 \u0926\u0915\u094d\u0937\u093f\u0928', svg_d: '\u091c\u094b\u0928 D \u2014 \u092a\u0936\u094d\u091a\u093f\u092e',
        },
    };

    // ─── Init ────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        initParticles();
        animateCounters();
        translateUI(currentLang);

        fetch(API + '/api/csrf-token')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.csrf_token) {
                    document.getElementById('csrf-token').setAttribute('content', data.csrf_token);
                }
            })
            .catch(function () {});

        setTimeout(function () {
            var loader = document.getElementById('app-loader');
            loader.classList.add('hidden');
            loader.setAttribute('aria-busy', 'false');
            loader.setAttribute('aria-live', 'off');
            var t = I18N[currentLang] || I18N.en;
            showToast(t.toast_ready, 'success');
        }, 2200);

        loadCrowdData();
        loadTransportData();
        loadEcoData();
        loadFacilityMap();
        setupChat();
        setupTabs();

        // ─── AI Translation Cache ──────────────────────────────
        var aiTranslationCache = {};

        function loadAITranslations(lang) {
            if (aiTranslationCache[lang]) {
                I18N[lang] = aiTranslationCache[lang];
                return Promise.resolve();
            }
            var en = I18N.en;
            var texts = {};
            Object.keys(en).forEach(function (k) { texts[k] = en[k]; });
            return fetch(API + '/api/i18n/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texts: texts, target_lang: lang })
            })
            .then(function (r) { return r.json(); })
            .then(function (result) {
                if (result.status === 'success' && result.data) {
                    var merged = {};
                    Object.keys(en).forEach(function (k) {
                        merged[k] = result.data[k] || en[k];
                    });
                    I18N[lang] = merged;
                    aiTranslationCache[lang] = merged;
                }
            })
            .catch(function () {
                // Fallback to hardcoded translations
            });
        }

        document.getElementById('lang-select').addEventListener('change', function () {
            currentLang = this.value;
            if (currentLang === 'en') {
                translateUI(currentLang);
            } else {
                loadAITranslations(currentLang).then(function () {
                    translateUI(currentLang);
                });
            }
            loadTransportData();
            loadEcoData();
            loadFacilityMap();
            if (document.getElementById('view-command').classList.contains('active')) {
                loadAlerts();
                loadStaffGrid();
                loadAIInsights();
            }
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
        var svgMap = { 'svg-zone-a': 'svg_a', 'svg-zone-b': 'svg_b', 'svg-zone-c': 'svg_c', 'svg-zone-d': 'svg_d' };
        Object.keys(svgMap).forEach(function (id) {
            var el = document.getElementById(id);
            if (el && t[svgMap[id]]) el.textContent = t[svgMap[id]];
        });
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
        document.querySelectorAll('.view').forEach(function (v) {
            v.classList.remove('active');
            v.setAttribute('aria-hidden', 'true');
        });
        var target = document.getElementById('view-' + view);
        if (target) {
            target.classList.add('active');
            target.removeAttribute('aria-hidden');
        }
        document.querySelectorAll('.nav-pill').forEach(function (b) {
            var isActive = b.dataset.view === view;
            b.classList.toggle('active', isActive);
            b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
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
            var isActive = t.dataset.tab === name;
            t.classList.toggle('active', isActive);
            t.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });
        document.querySelectorAll('.tab-content').forEach(function (p) {
            p.classList.remove('active');
            p.setAttribute('aria-hidden', 'true');
        });
        var panel = document.getElementById('tab-' + name);
        if (panel) {
            panel.classList.add('active');
            panel.removeAttribute('aria-hidden');
        }
    };

    // ─── Accessibility Toggle ────────────────────────────────
    window.toggleAccessibility = function () {
        a11yMode = !a11yMode;
        document.body.classList.toggle('a11y', a11yMode);
        var btn = document.getElementById('a11y-btn');
        btn.classList.toggle('active', a11yMode);
        btn.setAttribute('aria-expanded', a11yMode ? 'true' : 'false');
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

        var csrfToken = document.getElementById('csrf-token').getAttribute('content') || '';
        fetch(API + '/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
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
        var t = I18N[currentLang] || I18N.en;
        var e = I18N.en;
        function tr(key) { return t[key] || e[key]; }
        var zoneMap = { A: tr('zone_a'), B: tr('zone_b'), C: tr('zone_c'), D: tr('zone_d') };
        var html = '';

        Object.keys(zones).forEach(function (zid) {
            var z = zones[zid];
            var pct = z.percentage || 0;
            var level = z.level || 'low';
            var zoneName = zoneMap[zid] || (z.name || 'Zone ' + zid);
            var levelLabel = tr('level_' + level);

            html +=
                '<div class="zone-card" data-level="' + level + '">' +
                    '<div class="zone-top">' +
                        '<span class="zone-name">' + zoneName + '</span>' +
                        '<span class="zone-badge ' + level + '">' + levelLabel + '</span>' +
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
        var t = I18N[currentLang] || I18N.en;
        var e = I18N.en;
        function tr(key) { return t[key] || e[key]; }
        el.innerHTML =
            '<div class="info-card"><h4><i class="fas fa-parking"></i> ' + tr('tr_parking') + '</h4>' +
            '<div class="info-row"><span>' + tr('tr_lot_a') + '</span><span>$40</span><span class="badge badge-green">' + tr('tr_ev') + '</span></div>' +
            '<div class="info-row"><span>' + tr('tr_lot_b') + '</span><span>$35</span><span class="badge badge-red">' + tr('tr_no_ev') + '</span></div>' +
            '<div class="info-row"><span>' + tr('tr_lot_c') + '</span><span>$38</span><span class="badge badge-green">' + tr('tr_ev') + '</span></div>' +
            '</div>' +
            '<div class="info-card"><h4><i class="fas fa-train"></i> ' + tr('tr_transit') + '</h4>' +
            '<div class="info-row"><span>' + tr('tr_metlife') + '</span><span>0.5 km</span><span>' + tr('tr_every') + ' 10 ' + tr('tr_min') + '</span></div>' +
            '<div class="info-row"><span>' + tr('tr_bus') + '</span><span>1.2 km</span><span>' + tr('tr_every') + ' 15 ' + tr('tr_min') + '</span></div>' +
            '</div>' +
            '<div class="info-card"><h4><i class="fas fa-car"></i> ' + tr('tr_rideshare') + '</h4>' +
            '<div class="info-row"><span>' + tr('tr_pickup') + '</span><span>' + tr('tr_west') + '</span></div>' +
            '<div class="info-row"><span>' + tr('tr_dropoff') + '</span><span>' + tr('tr_north') + '</span></div>' +
            '</div>';
    }

    // ─── Eco ─────────────────────────────────────────────────
    function loadEcoData() {
        var el = document.getElementById('eco-list');
        if (!el) return;
        var t = I18N[currentLang] || I18N.en;
        var e = I18N.en;
        function tr(key) { return t[key] || e[key]; }
        el.innerHTML =
            '<div class="eco-highlight"><div><h4>' + tr('eco_station_n') + '</h4><p style="font-size:.7rem;color:var(--text-3)">' + tr('eco_materials_1') + '</p></div><span class="eco-pts">+50 ' + tr('eco_pts') + '</span></div>' +
            '<div class="eco-highlight"><div><h4>' + tr('eco_station_e') + '</h4><p style="font-size:.7rem;color:var(--text-3)">' + tr('eco_materials_2') + '</p></div><span class="eco-pts">+30 ' + tr('eco_pts') + '</span></div>' +
            '<div class="eco-highlight"><div><h4>' + tr('eco_station_s') + '</h4><p style="font-size:.7rem;color:var(--text-3)">' + tr('eco_materials_3') + '</p></div><span class="eco-pts">+75 ' + tr('eco_pts') + '</span></div>' +
            '<div class="info-card"><h4><i class="fas fa-leaf"></i> ' + tr('eco_tips') + '</h4>' +
            '<div class="info-row"><span>' + tr('eco_bike') + '</span><span class="badge badge-green">+200 ' + tr('eco_pts') + '</span></div>' +
            '<div class="info-row"><span>' + tr('eco_transit') + '</span><span class="badge badge-green">+100 ' + tr('eco_pts') + '</span></div>' +
            '<div class="info-row"><span>' + tr('eco_reusable') + '</span><span class="badge badge-green">+75 ' + tr('eco_pts') + '</span></div>' +
            '</div>';
    }

    // ─── Facility Map ────────────────────────────────────────
    function loadFacilityMap() {
        var t = I18N[currentLang] || I18N.en;
        var e = I18N.en;
        function tr(key) { return t[key] || e[key]; }
        var facilities = [
            { icon: 'fa-door-open', name: tr('fac_gate1'), accessible: true },
            { icon: 'fa-door-open', name: tr('fac_gate2'), accessible: true },
            { icon: 'fa-door-open', name: tr('fac_gate3'), accessible: true },
            { icon: 'fa-door-open', name: tr('fac_gate4'), accessible: true },
            { icon: 'fa-restroom', name: tr('fac_rest_n'), accessible: true },
            { icon: 'fa-restroom', name: tr('fac_rest_e'), accessible: true },
            { icon: 'fa-utensils', name: tr('fac_food_n'), extra: tr('fac_food_n_sub') },
            { icon: 'fa-utensils', name: tr('fac_food_e'), extra: tr('fac_food_e_sub') },
            { icon: 'fa-utensils', name: tr('fac_food_s'), extra: tr('fac_food_s_sub') },
            { icon: 'fa-utensils', name: tr('fac_food_w'), extra: tr('fac_food_w_sub') },
            { icon: 'fa-medkit', name: tr('fac_med_n') },
            { icon: 'fa-medkit', name: tr('fac_med_s') },
            { icon: 'fa-recycle', name: tr('fac_eco_n') },
            { icon: 'fa-recycle', name: tr('fac_eco_s') }
        ];

        var el = document.getElementById('facility-list');
        if (!el) return;
        var html = '';
        facilities.forEach(function (f) {
            var badge = f.accessible ? '<span class="badge badge-green">' + tr('fac_accessible') + '</span>' : '';
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
        var t = I18N[currentLang] || I18N.en;
        var e = I18N.en;
        function tr(key) { return t[key] || e[key]; }
        var alerts = [
            { type: 'warning', icon: 'fa-exclamation-triangle', text: tr('alert_1'), time: tr('alert_1_time') },
            { type: 'success', icon: 'fa-check-circle', text: tr('alert_2'), time: tr('alert_2_time') },
            { type: 'info', icon: 'fa-info-circle', text: tr('alert_3'), time: tr('alert_3_time') },
            { type: 'danger', icon: 'fa-bell', text: tr('alert_4'), time: tr('alert_4_time') },
            { type: 'success', icon: 'fa-check-circle', text: tr('alert_5'), time: tr('alert_5_time') }
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
                var t = I18N[currentLang] || I18N.en;
                var e = I18N.en;
                function tr(key) { return t[key] || e[key]; }
                var depts = data.data.departments;
                var deptMap = { cleaning: tr('staff_cleaning'), crowd_mgmt: tr('staff_crowd'), guest_services: tr('staff_guest'), medical: tr('staff_medical'), security: tr('staff_security') };
                var html = '';
                Object.keys(depts).forEach(function (key) {
                    var d = depts[key];
                    var pct = Math.round(d.deployed / d.total * 100);
                    var label = deptMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
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
                var t = I18N[currentLang] || I18N.en;
                var e = I18N.en;
                function tr(key) { return t[key] || e[key]; }
                var suggestions = data.data.optimization_suggestions || [];
                var html = '';
                suggestions.forEach(function (s) {
                    html +=
                        '<div class="ai-item">' +
                            '<div class="ai-type"><i class="fas fa-brain"></i> ' + tr('ai_recommendation') + '</div>' +
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
