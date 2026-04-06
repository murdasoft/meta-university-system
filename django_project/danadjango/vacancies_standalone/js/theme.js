/**
 * Светлая / тёмная тема. localStorage: jobPortalTheme = light | dark
 * Раннее применение — до отрисовки, скрипт подключать в <head>.
 */
(function (global) {
  var KEY = 'jobPortalTheme';

  function fromStorage() {
    try {
      var v = localStorage.getItem(KEY);
      if (v === 'dark' || v === 'light') return v;
    } catch (e) {}
    return null;
  }

  function fromPrefers() {
    try {
      if (global.matchMedia && global.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    } catch (e) {}
    return 'light';
  }

  function get() {
    var s = fromStorage();
    return s != null ? s : fromPrefers();
  }

  function applyToDocument(theme) {
    var t = theme === 'dark' ? 'dark' : 'light';
    if (global.document && global.document.documentElement) {
      global.document.documentElement.setAttribute('data-theme', t);
    }
  }

  function applyMeta(theme) {
    var t = theme === 'dark' ? 'dark' : 'light';
    if (!global.document) return;
    var meta = global.document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute('content', t === 'dark' ? '#0f1412' : '#eef2f0');
    }
  }

  var JobPortalTheme = {
    get: get,
    set: function (mode) {
      if (mode !== 'dark' && mode !== 'light') mode = 'light';
      try {
        localStorage.setItem(KEY, mode);
      } catch (e) {}
      applyToDocument(mode);
      applyMeta(mode);
      if (global.document) {
        global.document.dispatchEvent(
          new CustomEvent('jobportal:themechange', { detail: { theme: mode } }),
        );
      }
    },
    toggle: function () {
      JobPortalTheme.set(JobPortalTheme.get() === 'dark' ? 'light' : 'dark');
    },
    init: function () {
      applyToDocument(JobPortalTheme.get());
      applyMeta(JobPortalTheme.get());
    },
    mountToggle: function (el) {
      if (!el || el.getAttribute('data-theme-mounted')) return;
      el.setAttribute('data-theme-mounted', '1');
      var btn = global.document.createElement('button');
      btn.type = 'button';
      btn.className = 'mock-theme-toggle';
      btn.innerHTML =
        '<span class="mock-theme-toggle__track" aria-hidden="true">' +
        '<span class="mock-theme-toggle__thumb"></span>' +
        '</span>';
      el.appendChild(btn);

      function refresh() {
        var dark = JobPortalTheme.get() === 'dark';
        btn.classList.toggle('mock-theme-toggle--dark', dark);
        btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
        if (global.JobPortalI18n) {
          btn.setAttribute(
            'aria-label',
            dark
              ? JobPortalI18n.t('shell.themeAriaLight')
              : JobPortalI18n.t('shell.themeAriaDark'),
          );
          btn.setAttribute(
            'title',
            dark ? JobPortalI18n.t('shell.themeToLight') : JobPortalI18n.t('shell.themeToDark'),
          );
        } else {
          btn.setAttribute('aria-label', dark ? 'Светлая тема' : 'Тёмная тема');
          btn.setAttribute('title', dark ? 'Светлая тема' : 'Тёмная тема');
        }
      }

      refresh();
      btn.addEventListener('click', function () {
        JobPortalTheme.toggle();
      });
      global.document.addEventListener('jobportal:themechange', refresh);
      global.document.addEventListener('jobportal:langchange', refresh);
    },
  };

  var initial = get();
  applyToDocument(initial);
  if (global.document && global.document.querySelector) {
    applyMeta(initial);
  }

  global.JobPortalTheme = JobPortalTheme;

  if (global.document && global.document.readyState === 'loading') {
    global.document.addEventListener('DOMContentLoaded', function () {
      JobPortalTheme.init();
    });
  } else if (global.document) {
    JobPortalTheme.init();
  }
})(typeof window !== 'undefined' ? window : this);
