/**
 * StadiumIQ v3.0 — AI Smart Stadium Assistant
 * Google Gemini 2.5 Flash powered with stunning UI
 */
(function () {
    'use strict';

    const API = '';
    let currentLang = 'en';
    let a11yMode = false;
    let crowdChart = null;
    let sentimentChart = null;

    // ─── Init ────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        createParticles();
        setTimeout(function () {
            document.getElementById('app-loader').classList.add('hidden');
            showToast('StadiumIQ is ready! Ask me anything.', 'success');
        }, 2200);

        loadCrowdData();
        loadTransportData();
        loadEcoData();
        loadFacilityMap();
        setupChat();
        setupTabs();

        document.getElementById('lang-select').addEventListener('change', function () {
            currentLang = this.value;
            showToast('Language changed to ' + this.options[this.selectedIndex].text, 'info');
        });

        setInterval(refreshCrowdData, 6000);
    });

    // ─── Particle System ─────────────────────────────────────
    function createParticles() {
        var container = document.createElement('div');
        container.className = 'particles';
        document.body.appendChild(container);

        for (var i = 0; i < 50; i++) {
            var p = document.createElement('div');
            p.className = 'particle';
            p.style.left = Math.random() * 100 + '%';
            p.style.animationDuration = (Math.random() * 15 + 10) + 's';
            p.style.animationDelay = (Math.random() * 10) + 's';
            p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
            var colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899'];
            p.style.background = colors[Math.floor(Math.random() * colors.length)];
            container.appendChild(p);
        }
    }

    // ─── Toast Notifications ─────────────────────────────────
    window.showToast = function (message, type) {
        type = type || 'info';
        var existing = document.querySelector('.toast');
        if (existing) existing.remove();

        var toast = document.createElement('div');
        toast.className = 'toast ' + type;

        var icons = { success: 'fa-check-circle', warning: 'fa-exclamation-triangle', error: 'fa-times-circle', info: 'fa-info-circle' };
        toast.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '"></i><span>' + message + '</span>';
        document.body.appendChild(toast);

        setTimeout(function () {
            toast.style.animation = 'toastOut 0.3s ease forwards';
            setTimeout(function () { toast.remove(); }, 300);
        }, 3500);
    };

    // ─── View Switching ──────────────────────────────────────
    window.switchView = function (view) {
        document.querySelectorAll('.view').forEach(function (v) { v.classList.remove('active'); });
        document.getElementById('view-' + view).classList.add('active');
        document.querySelectorAll('.nav-btn').forEach(function (b) {
            b.classList.toggle('active', b.dataset.view === view);
        });
        if (view === 'command') loadCommandCenter();
    };

    // ─── Tab Switching ───────────────────────────────────────
    function setupTabs() {
        document.querySelectorAll('.info-tab').forEach(function (tab) {
            tab.addEventListener('click', function () {
                var name = this.dataset.tab;
                switchInfoTab(name);
            });
        });
    }

    window.switchInfoTab = function (name) {
        document.querySelectorAll('.info-tab').forEach(function (t) {
            t.classList.toggle('active', t.dataset.tab === name);
        });
        document.querySelectorAll('.info-panel').forEach(function (p) { p.classList.remove('active'); });
        var panel = document.getElementById('info-' + name);
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
        if (latency) footer += ' · ' + source + ' · ' + latency + 'ms';
        footer += '</span>';

        div.innerHTML =
            '<div class="msg-avatar"><i class="fas ' + icon + '"></i></div>' +
            '<div class="msg-body"><div class="msg-content">' + formatMd(content) + '</div>' + footer + '</div>';

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
            '<div class="msg-body"><div class="msg-content">' +
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
                        cells.map(function (c) { return '<span style="padding:3px 5px;background:rgba(30,41,59,0.5);border-radius:4px;border:1px solid var(--glass-border)">' + c.trim() + '</span>'; }).join('') + '</div>';
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
        var html = '';

        Object.keys(zones).forEach(function (zid) {
            var z = zones[zid];
            var pct = z.percentage || 0;
            var level = z.level || 'low';

            html +=
                '<div class="zone-card">' +
                    '<div class="zone-card-top">' +
                        '<span class="zone-card-name">' + (z.name || 'Zone ' + zid) + '</span>' +
                        '<span class="zone-badge ' + level + '">' + level + '</span>' +
                    '</div>' +
                    '<div class="zone-bar"><div class="zone-bar-fill ' + level + '" style="width:' + pct + '%"></div></div>' +
                    '<div class="zone-card-stats">' +
                        '<span>' + (z.occupancy || 0).toLocaleString() + ' / ' + (z.capacity || 0).toLocaleString() + '</span>' +
                        '<span>' + pct + '%</span>' +
                    '</div>' +
                    '<div class="zone-card-stats" style="margin-top:0.3rem;font-size:0.62rem">' +
                        '<span>↗ +' + (z.inflow || 0) + ' in</span>' +
                        '<span>↙ -' + (z.outflow || 0) + ' out</span>' +
                        '<span>' + (z.trend || 'stable') + '</span>' +
                    '</div>' +
                '</div>';
        });

        container.innerHTML = html;

        // Update SVG zones
        Object.keys(zones).forEach(function (zid) {
            var z = zones[zid];
            var el = document.getElementById('zone-' + zid.toLowerCase() + '-svg');
            if (el) {
                var colors = { low: '#10b981', moderate: '#f59e0b', high: '#f97316', critical: '#ef4444', overflow: '#dc2626' };
                el.setAttribute('fill', colors[z.level] || '#3b82f6');
                el.style.opacity = 0.3 + (z.percentage / 100) * 0.7;
            }
        });
    }

    // ─── Transport ───────────────────────────────────────────
    function loadTransportData() {
        document.getElementById('transport-list').innerHTML =
            '<div class="transport-card"><h4><i class="fas fa-parking"></i> Parking</h4>' +
            '<div class="transport-row"><span>Lot A (North)</span><span>$40</span><span class="badge badge-success">EV Charging</span></div>' +
            '<div class="transport-row"><span>Lot B (East)</span><span>$35</span><span class="badge badge-danger">No EV</span></div>' +
            '<div class="transport-row"><span>Lot C (South)</span><span>$38</span><span class="badge badge-success">EV Charging</span></div>' +
            '</div>' +
            '<div class="transport-card"><h4><i class="fas fa-train"></i> Public Transit</h4>' +
            '<div class="transport-row"><span>MetLife Station</span><span>0.5 km</span><span>Every 10 min</span></div>' +
            '<div class="transport-row"><span>Bus Terminal</span><span>1.2 km</span><span>Every 15 min</span></div>' +
            '</div>' +
            '<div class="transport-card"><h4><i class="fas fa-car"></i> Rideshare</h4>' +
            '<div class="transport-row"><span>Pickup</span><span>West Zone</span></div>' +
            '<div class="transport-row"><span>Drop-off</span><span>North Zone</span></div>' +
            '</div>';
    }

    // ─── Eco ─────────────────────────────────────────────────
    function loadEcoData() {
        document.getElementById('eco-list').innerHTML =
            '<div class="eco-card"><div><h4>Eco Station North</h4><p style="font-size:0.72rem;color:var(--text-muted)">Plastic, Paper, Glass</p></div><span class="eco-points">+50 pts</span></div>' +
            '<div class="eco-card"><div><h4>Eco Station East</h4><p style="font-size:0.72rem;color:var(--text-muted)">Plastic, Paper</p></div><span class="eco-points">+30 pts</span></div>' +
            '<div class="eco-card"><div><h4>Eco Station South</h4><p style="font-size:0.72rem;color:var(--text-muted)">All + Food Waste</p></div><span class="eco-points">+75 pts</span></div>' +
            '<div class="transport-card" style="margin-top:0.75rem"><h4><i class="fas fa-leaf"></i> Green Tips</h4>' +
            '<div class="transport-row"><span>Bike to stadium</span><span class="badge badge-success">+200 pts</span></div>' +
            '<div class="transport-row"><span>Public transit</span><span class="badge badge-success">+100 pts</span></div>' +
            '<div class="transport-row"><span>Reusable container</span><span class="badge badge-success">+75 pts</span></div>' +
            '</div>';
    }

    // ─── Facility Map ────────────────────────────────────────
    function loadFacilityMap() {
        var facilities = [
            { icon: 'fa-door-open', name: 'Gate E1 — Main North', accessible: true },
            { icon: 'fa-door-open', name: 'Gate E2 — East', accessible: true },
            { icon: 'fa-door-open', name: 'Gate E3 — South', accessible: true },
            { icon: 'fa-door-open', name: 'Gate E4 — VIP', accessible: true },
            { icon: 'fa-restroom', name: 'Restroom North', accessible: true },
            { icon: 'fa-restroom', name: 'Restroom East', accessible: true },
            { icon: 'fa-utensils', name: 'Food Court North', extra: 'American, Mexican' },
            { icon: 'fa-utensils', name: 'Food Court East', extra: 'Asian, Italian' },
            { icon: 'fa-utensils', name: 'Food Court South', extra: 'Halal, Vegan' },
            { icon: 'fa-utensils', name: 'Food Court West', extra: 'Burgers, Pizza' },
            { icon: 'fa-medkit', name: 'Medical Station North' },
            { icon: 'fa-medkit', name: 'Medical Station South' },
            { icon: 'fa-recycle', name: 'Eco Station North' },
            { icon: 'fa-recycle', name: 'Eco Station South' },
        ];

        var html = '';
        facilities.forEach(function (f) {
            var badge = f.accessible ? '<span class="badge badge-success">Accessible</span>' : '';
            var extra = f.extra ? '<div style="font-size:0.65rem;color:var(--text-dim)">' + f.extra + '</div>' : '';
            html +=
                '<div class="transport-card" style="display:flex;gap:0.6rem;align-items:center">' +
                    '<i class="fas ' + f.icon + '" style="color:var(--primary);font-size:1rem;width:20px;text-align:center"></i>' +
                    '<div style="flex:1"><div style="font-size:0.8rem;font-weight:600">' + f.name + '</div>' + extra + '</div>' +
                    badge +
                '</div>';
        });
        document.getElementById('facility-list').innerHTML = html;
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
                var kpis = data.data;
                var icons = ['fa-users', 'fa-door-open', 'fa-clock', 'fa-shield-alt', 'fa-leaf', 'fa-exclamation-circle'];
                var html = '';
                Object.keys(kpis).forEach(function (key, i) {
                    var kpi = kpis[key];
                    var label = key.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                    html +=
                        '<div class="kpi-card">' +
                            '<div class="kpi-label"><i class="fas ' + (icons[i] || 'fa-chart-line') + '"></i> ' + label + '</div>' +
                            '<div class="kpi-value">' + kpi.value + '<span style="font-size:0.6rem;color:var(--text-dim)">' + kpi.unit + '</span></div>' +
                            '<div class="kpi-sub">Target: ' + kpi.target + kpi.unit + ' · ' + kpi.trend + '</div>' +
                        '</div>';
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
                    var color = r.risk_level === 'critical' ? 'var(--danger)' : r.risk_level === 'high' ? 'var(--warning)' : r.risk_level === 'moderate' ? 'var(--accent)' : 'var(--success)';
                    html +=
                        '<div class="risk-item">' +
                            '<div class="risk-zone">Zone ' + zid + '</div>' +
                            '<div class="risk-score" style="color:' + color + '">' + r.risk_score + '%</div>' +
                            '<div class="risk-level" style="color:' + color + '">' + r.risk_level + '</div>' +
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
            { type: 'success', icon: 'fa-check-circle', text: 'Medical response time: 2.1 min average', time: '15 min ago' },
        ];
        var html = '';
        alerts.forEach(function (a) {
            html +=
                '<div class="alert-item ' + a.type + '">' +
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
                            '<div class="staff-bar"><div class="staff-bar-fill" style="width:' + pct + '%"></div></div>' +
                            '<span class="staff-count">' + d.deployed + '/' + d.total + '</span>' +
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
                        '<div class="insight-item">' +
                            '<div class="insight-type"><i class="fas fa-brain"></i> AI Recommendation</div>' +
                            '<div class="insight-text">' + s + '</div>' +
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
                var colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
                var datasets = Object.keys(zones).map(function (z, i) {
                    return {
                        label: 'Zone ' + z,
                        data: zones[z],
                        borderColor: colors[i],
                        backgroundColor: colors[i] + '20',
                        fill: true, tension: 0.4, borderWidth: 2,
                    };
                });

                if (crowdChart) crowdChart.destroy();
                crowdChart = new Chart(ctx, {
                    type: 'line',
                    data: { labels: labels, datasets: datasets },
                    options: {
                        responsive: true,
                        plugins: { legend: { labels: { color: '#94a3b8', font: { size: 10 } } } },
                        scales: {
                            x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: '#1e293b' } },
                            y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: '#1e293b' }, min: 0, max: 100 },
                        },
                    },
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
                            borderRadius: 6,
                        }],
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { display: false } },
                            y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: '#1e293b' }, min: 0, max: 10 },
                        },
                    },
                });
            });
    }

})();
