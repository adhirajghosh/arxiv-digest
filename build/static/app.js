/* build/static/app.js */
(function () {
    'use strict';

    // ── Theme Toggle ──
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');

    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('arxiv-digest-theme', theme);
    }

    // Init theme from localStorage or system preference
    const saved = localStorage.getItem('arxiv-digest-theme');
    if (saved) {
        setTheme(saved);
    } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
        setTheme('light');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = html.getAttribute('data-theme') || 'dark';
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    // ── Calendar Popover ──
    const dateToggle = document.getElementById('date-toggle');
    const calendarPopover = document.getElementById('calendar-popover');
    const calendarGrid = document.getElementById('calendar-grid');
    const calendarLabel = document.getElementById('calendar-month-label');
    const calendarPrev = document.getElementById('calendar-prev');
    const calendarNext = document.getElementById('calendar-next');
    const calendarLatest = document.getElementById('calendar-latest');
    const calendarCountNum = document.getElementById('calendar-count-num');

    if (dateToggle && calendarPopover && calendarGrid) {
        // Parse available dates (JSON array of YYYY-MM-DD strings, newest first).
        let availableDates = [];
        try {
            availableDates = JSON.parse(calendarPopover.getAttribute('data-available-dates') || '[]');
        } catch (e) { availableDates = []; }

        const availableSet = new Set(availableDates);
        const currentDateStr = calendarPopover.getAttribute('data-current-date');
        if (calendarCountNum) calendarCountNum.textContent = availableDates.length;

        // View state
        let viewYear, viewMonth; // 0-indexed month
        if (currentDateStr) {
            const parts = currentDateStr.split('-');
            viewYear = parseInt(parts[0], 10);
            viewMonth = parseInt(parts[1], 10) - 1;
        } else {
            const now = new Date();
            viewYear = now.getFullYear();
            viewMonth = now.getMonth();
        }

        const MONTH_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December'];

        function pad(n) { return n < 10 ? '0' + n : '' + n; }
        function fmt(y, m, d) { return y + '-' + pad(m + 1) + '-' + pad(d); }

        function hasDigestInMonth(y, m) {
            const prefix = y + '-' + pad(m + 1) + '-';
            for (let i = 0; i < availableDates.length; i++) {
                if (availableDates[i].indexOf(prefix) === 0) return true;
            }
            return false;
        }

        function earliestMonth() {
            if (availableDates.length === 0) return null;
            const last = availableDates[availableDates.length - 1]; // oldest
            const p = last.split('-');
            return { y: parseInt(p[0], 10), m: parseInt(p[1], 10) - 1 };
        }

        function latestMonth() {
            if (availableDates.length === 0) return null;
            const first = availableDates[0]; // newest
            const p = first.split('-');
            return { y: parseInt(p[0], 10), m: parseInt(p[1], 10) - 1 };
        }

        function renderCalendar() {
            calendarLabel.textContent = MONTH_NAMES[viewMonth] + ' ' + viewYear;

            // Previous/next month enablement
            const earliest = earliestMonth();
            const latest = latestMonth();
            const atEarliest = earliest && viewYear === earliest.y && viewMonth === earliest.m;
            const atLatest = latest && viewYear === latest.y && viewMonth === latest.m;
            calendarPrev.disabled = !earliest || atEarliest;
            calendarNext.disabled = !latest || atLatest;

            // Compute grid — Monday-first weeks
            const firstOfMonth = new Date(viewYear, viewMonth, 1);
            // JS getDay(): 0 = Sunday. We want Monday-first: (getDay() + 6) % 7.
            const startOffset = (firstOfMonth.getDay() + 6) % 7;
            const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
            const todayStr = (function () {
                const n = new Date();
                return fmt(n.getFullYear(), n.getMonth(), n.getDate());
            })();

            calendarGrid.innerHTML = '';

            // Leading empty cells
            for (let i = 0; i < startOffset; i++) {
                const cell = document.createElement('div');
                cell.className = 'calendar-cell empty';
                calendarGrid.appendChild(cell);
            }

            for (let d = 1; d <= daysInMonth; d++) {
                const dateStr = fmt(viewYear, viewMonth, d);
                const hasDigest = availableSet.has(dateStr);
                const isCurrent = dateStr === currentDateStr;
                const isToday = dateStr === todayStr;

                let el;
                if (hasDigest) {
                    el = document.createElement('a');
                    el.href = dateStr + '.html';
                    el.setAttribute('aria-label', 'View digest for ' + dateStr);
                } else {
                    el = document.createElement('div');
                }
                el.className = 'calendar-cell';
                if (hasDigest) el.classList.add('has-digest');
                else el.classList.add('no-digest');
                if (isCurrent) el.classList.add('active');
                if (isToday) el.classList.add('today');
                el.textContent = d;
                calendarGrid.appendChild(el);
            }
        }

        function openCalendar() {
            calendarPopover.classList.add('open');
            dateToggle.setAttribute('aria-expanded', 'true');
            renderCalendar();
        }
        function closeCalendar() {
            calendarPopover.classList.remove('open');
            dateToggle.setAttribute('aria-expanded', 'false');
        }

        dateToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            if (calendarPopover.classList.contains('open')) closeCalendar();
            else openCalendar();
        });

        calendarPopover.addEventListener('click', function (e) { e.stopPropagation(); });

        document.addEventListener('click', closeCalendar);
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeCalendar();
        });

        calendarPrev.addEventListener('click', function () {
            viewMonth -= 1;
            if (viewMonth < 0) { viewMonth = 11; viewYear -= 1; }
            renderCalendar();
        });
        calendarNext.addEventListener('click', function () {
            viewMonth += 1;
            if (viewMonth > 11) { viewMonth = 0; viewYear += 1; }
            renderCalendar();
        });
        if (calendarLatest) {
            calendarLatest.addEventListener('click', function () {
                if (availableDates.length > 0) {
                    window.location.href = availableDates[0] + '.html';
                }
            });
        }
    }

    // ── Search ──
    const searchToggle = document.getElementById('search-toggle');
    const searchBar = document.getElementById('search-bar');
    const searchInput = document.getElementById('search-input');
    const searchClose = document.getElementById('search-close');
    const paperCards = document.querySelectorAll('.paper-card');

    if (searchToggle && searchBar) {
        searchToggle.addEventListener('click', function () {
            searchBar.classList.toggle('open');
            if (searchBar.classList.contains('open')) {
                searchInput.focus();
            } else {
                searchInput.value = '';
                filterBySearch('');
            }
        });
    }

    if (searchClose) {
        searchClose.addEventListener('click', function () {
            searchBar.classList.remove('open');
            searchInput.value = '';
            filterBySearch('');
        });
    }

    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function () {
                filterBySearch(searchInput.value);
            }, 150);
        });
    }

    function filterBySearch(query) {
        var q = query.toLowerCase().trim();
        paperCards.forEach(function (card) {
            if (!q) {
                card.setAttribute('data-search-hidden', 'false');
            } else {
                var title = (card.querySelector('.paper-title') || {}).textContent || '';
                var tldr = (card.querySelector('.paper-tldr') || {}).textContent || '';
                var match = title.toLowerCase().indexOf(q) !== -1 || tldr.toLowerCase().indexOf(q) !== -1;
                card.setAttribute('data-search-hidden', match ? 'false' : 'true');
            }
        });
        applyVisibility();
    }

    // ── Topic Filtering ──
    var topicPills = document.querySelectorAll('.topic-pill');
    var activeTopic = 'all';

    topicPills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            topicPills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');
            activeTopic = pill.getAttribute('data-topic');
            applyVisibility();
            // Update URL hash
            if (activeTopic === 'all') {
                history.replaceState(null, '', window.location.pathname);
            } else {
                history.replaceState(null, '', '#' + encodeURIComponent(activeTopic));
            }
        });
    });

    // Restore filter from URL hash
    if (window.location.hash) {
        var hashTopic = decodeURIComponent(window.location.hash.slice(1));
        topicPills.forEach(function (pill) {
            if (pill.getAttribute('data-topic') === hashTopic) {
                pill.click();
            }
        });
    }

    function applyVisibility() {
        paperCards.forEach(function (card) {
            var topicMatch = activeTopic === 'all' || (card.getAttribute('data-topics') || '').indexOf(activeTopic) !== -1;
            var searchMatch = card.getAttribute('data-search-hidden') !== 'true';
            card.setAttribute('data-hidden', !(topicMatch && searchMatch));
        });
    }

    // ── Expand/Collapse ──
    document.querySelectorAll('.expand-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.getAttribute('data-target');
            var target = document.getElementById(targetId);
            if (!target) return;
            var isOpen = target.classList.contains('open');
            target.classList.toggle('open');
            btn.classList.toggle('expanded');
            // Update button text
            var text = btn.textContent.trim();
            if (isOpen) {
                btn.innerHTML = btn.innerHTML.replace(/Hide/, 'Show');
            } else {
                btn.innerHTML = btn.innerHTML.replace(/Show/, 'Hide');
            }
        });
    });

    // ── Expand Authors ──
    document.querySelectorAll('.expand-authors').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var card = btn.closest('.paper-card');
            var short = card.querySelector('.paper-authors');
            var full = card.querySelector('.paper-authors-full');
            short.classList.add('hidden');
            full.classList.remove('hidden');
        });
    });

    // ── Scroll Animations ──
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });

        paperCards.forEach(function (card) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            observer.observe(card);
        });
    }
})();
