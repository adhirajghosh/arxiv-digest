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

    // ── Date Dropdown ──
    const dateToggle = document.getElementById('date-toggle');
    const dateDropdown = document.getElementById('date-dropdown');

    if (dateToggle && dateDropdown) {
        dateToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            dateDropdown.classList.toggle('open');
        });

        document.addEventListener('click', function () {
            dateDropdown.classList.remove('open');
        });
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
