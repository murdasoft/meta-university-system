/**
 * Шапка, вторичная навигация, сессия пользователя (localStorage), подвал сайта.
 */
(function () {
  var LS_KEY = 'jobPortalDemoUser';

  window.JobPortalShell = {
    getUser: function () {
      try {
        var raw = localStorage.getItem(LS_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },
    setUser: function (u) {
      localStorage.setItem(LS_KEY, JSON.stringify(u));
    },
    clearUser: function () {
      localStorage.removeItem(LS_KEY);
    },
    logout: function () {
      this.clearUser();
      window.location.href = 'index.html';
    },
  };

  function pageFromBody() {
    return document.body.getAttribute('data-page') || '';
  }

  function t(key) {
    return window.JobPortalI18n ? JobPortalI18n.t(key) : key;
  }

  function renderTopActions() {
    var el = document.getElementById('top-actions');
    if (!el) return;
    var u = JobPortalShell.getUser();
    if (u) {
      var dash =
        u.role === 'seeker'
          ? 'seeker-dashboard.html'
          : u.role === 'employer'
            ? 'employer-dashboard.html'
            : 'admin-users.html';
      var label = u.role === 'admin' ? t('shell.admin') : t('shell.cabinet');
      el.innerHTML =
        '<span class="mock-user-pill" title="' +
        escapeHtml(u.email || '') +
        '">' +
        escapeHtml(u.display || '') +
        '</span>' +
        '<a class="mock-btn mock-btn--link" href="' +
        dash +
        '">' +
        label +
        '</a>' +
        '<button type="button" class="mock-btn mock-btn--ghost" id="demo-logout">' +
        t('shell.logout') +
        '</button>';
      document.getElementById('demo-logout').addEventListener('click', function () {
        JobPortalShell.logout();
      });
    } else {
      el.innerHTML =
        '<a class="mock-btn mock-btn--link" href="login.html">' +
        t('shell.login') +
        '</a>' +
        '<a class="mock-btn mock-btn--link mock-btn--primary" href="register.html">' +
        t('shell.register') +
        '</a>';
    }
  }

  function toggleAuthNavLink() {
    var authLink = document.getElementById('nav-auth-link');
    if (authLink) {
      authLink.style.display = JobPortalShell.getUser() ? 'none' : '';
    }
  }

  function setNavActive() {
    var page = pageFromBody();
    var map = {
      home: 'index.html',
      vacancies: 'vacancies.html',
      vacancy: 'vacancy.html',
      seeker: 'seeker-dashboard.html',
      employer: 'employer-dashboard.html',
      admin: 'admin-users.html',
      auth: 'login.html',
      contacts: 'contacts.html',
    };
    var target = map[page];
    var file = (window.location.pathname || '').split('/').pop() || '';
    if (file === 'login.html' || file === 'register.html') {
      var authLink = document.getElementById('nav-auth-link');
      if (authLink) authLink.classList.add('is-active');
      return;
    }
    document.querySelectorAll('.mock-demo-nav .mock-nav-item').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (target && href.indexOf(target) !== -1) a.classList.add('is-active');
    });
  }

  function escapeHtml(s) {
    if (!s) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function fillUserPlaceholders() {
    var u = JobPortalShell.getUser();
    document.querySelectorAll('[data-mock-user-display]').forEach(function (el) {
      el.textContent = u ? u.display || u.username || '' : '';
    });
  }

  function injectSiteFooter() {
    var el = document.querySelector('footer[data-site-footer]');
    if (!el) return;
    var y = String(new Date().getFullYear());
    el.innerHTML =
      '<div class="mock-footer__inner">' +
      '<nav class="mock-footer__links" aria-label="">' +
      '<a href="privacy.html">' +
      t('footer.privacy') +
      '</a>' +
      '<a href="offer.html">' +
      t('footer.offer') +
      '</a>' +
      '<a href="contacts.html">' +
      t('footer.contacts') +
      '</a>' +
      '</nav>' +
      '<div class="mock-footer__social">' +
      '<span class="mock-footer__social-title">' +
      t('footer.social') +
      '</span>' +
      '<a href="#" class="mock-footer__social-link">Telegram</a>' +
      '<a href="#" class="mock-footer__social-link">ВКонтакте</a>' +
      '<a href="#" class="mock-footer__social-link">Instagram</a>' +
      '</div>' +
      '<p class="mock-footer__copy">© ' +
      y +
      t('footer.copy') +
      '</p>' +
      '</div>';
    el.querySelectorAll('.mock-footer__social a[href="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
      });
    });
  }

  function wrapTopbarStart() {
    var inner = document.querySelector('.mock-topbar__inner');
    if (!inner || document.querySelector('.mock-topbar__start')) return;
    var brand = inner.querySelector('.mock-brand');
    var actions = inner.querySelector('#top-actions');
    if (!brand || !actions) return;
    var start = document.createElement('div');
    start.className = 'mock-topbar__start';
    brand.parentNode.insertBefore(start, brand);
    start.appendChild(brand);
    var controls = document.createElement('div');
    controls.className = 'mock-topbar__controls';
    var langHost = document.createElement('div');
    langHost.className = 'mock-topbar__lang';
    var themeHost = document.createElement('div');
    themeHost.className = 'mock-topbar__theme';
    controls.appendChild(langHost);
    controls.appendChild(themeHost);
    start.appendChild(controls);
    if (window.JobPortalI18n) {
      JobPortalI18n.mountLangSwitch(langHost);
    }
    if (window.JobPortalTheme) {
      JobPortalTheme.mountToggle(themeHost);
    }
    inner.appendChild(actions);
  }

  function syncBrandTitle() {
    document.querySelectorAll('.mock-brand').forEach(function (a) {
      a.textContent = t('brand.name');
    });
  }

  function onLangRefresh() {
    injectSiteFooter();
    renderTopActions();
    syncBrandTitle();
    if (window.JobPortalI18n) JobPortalI18n.apply();
  }

  document.addEventListener('DOMContentLoaded', function () {
    wrapTopbarStart();
    if (window.JobPortalI18n) {
      JobPortalI18n.apply();
    }
    syncBrandTitle();
    injectSiteFooter();
    renderTopActions();
    toggleAuthNavLink();
    setNavActive();
    fillUserPlaceholders();
    document.addEventListener('jobportal:langchange', onLangRefresh);
  });
})();
