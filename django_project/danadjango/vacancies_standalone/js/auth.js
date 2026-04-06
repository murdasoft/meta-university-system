/** Вход и регистрация с сохранением сессии в localStorage. */
(function () {
  var ACCOUNTS = {
    seeker: {
      password: 'demo123',
      role: 'seeker',
      display: 'Айдар Нурланов',
      email: 'seeker@demo.qazaqdana.kz',
    },
    employer: {
      password: 'demo123',
      role: 'employer',
      display: 'ТОО «Дана Демо»',
      email: 'hr@demo.qazaqdana.kz',
    },
    admin_demo: {
      password: 'demo123',
      role: 'admin',
      display: 'Администратор',
      email: 'admin@demo.qazaqdana.kz',
    },
  };

  function T(key) {
    return window.JobPortalI18n ? JobPortalI18n.t(key) : key;
  }

  function showMsg(el, text, kind) {
    if (!el) return;
    el.className = 'mock-messages';
    el.innerHTML =
      '<li class="mock-message mock-message--' +
      (kind || 'info') +
      '">' +
      text +
      '</li>';
    el.style.display = 'block';
  }

  function setLoginTab(role) {
    var seeker = document.getElementById('auth-hint-seeker');
    var employer = document.getElementById('auth-hint-employer');
    document.querySelectorAll('[data-auth-tab]').forEach(function (btn) {
      var on = btn.getAttribute('data-auth-tab') === role;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    if (seeker) seeker.hidden = role !== 'seeker';
    if (employer) employer.hidden = role !== 'employer';
  }

  function setRegisterTab(role) {
    var wrap = document.getElementById('reg-company-wrap');
    var hidden = document.getElementById('reg-role-value');
    var hs = document.getElementById('reg-hint-seeker');
    var he = document.getElementById('reg-hint-employer');
    if (hidden) hidden.value = role;
    document.querySelectorAll('[data-reg-tab]').forEach(function (btn) {
      var on = btn.getAttribute('data-reg-tab') === role;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    if (hs) hs.hidden = role !== 'seeker';
    if (he) he.hidden = role !== 'employer';
    if (wrap) {
      wrap.hidden = role !== 'employer';
      wrap.setAttribute('aria-hidden', role !== 'employer' ? 'true' : 'false');
    }
    var loginInput = document.getElementById('reg-user');
    if (loginInput) {
      loginInput.setAttribute(
        'data-i18n-placeholder',
        role === 'employer' ? 'auth.register.phLoginEmployer' : 'auth.register.phLoginSeeker',
      );
      if (window.JobPortalI18n) {
        loginInput.setAttribute(
          'placeholder',
          JobPortalI18n.t(
            role === 'employer' ? 'auth.register.phLoginEmployer' : 'auth.register.phLoginSeeker',
          ),
        );
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-auth-tab]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        setLoginTab(btn.getAttribute('data-auth-tab') || 'seeker');
      });
    });

    document.querySelectorAll('[data-reg-tab]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        setRegisterTab(btn.getAttribute('data-reg-tab') || 'seeker');
      });
    });

    document.addEventListener('jobportal:langchange', function () {
      var rv = document.getElementById('reg-role-value');
      if (rv) setRegisterTab(rv.value || 'seeker');
    });

    var loginForm = document.getElementById('form-login');
    if (loginForm) {
      setLoginTab('seeker');
      loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var u = (document.getElementById('login-user').value || '').trim().toLowerCase();
        var p = (document.getElementById('login-pass').value || '').trim();
        var acc = ACCOUNTS[u];
        var msg = document.getElementById('auth-messages');
        if (acc && acc.password === p) {
          JobPortalShell.setUser({
            username: u,
            role: acc.role,
            display: acc.display,
            email: acc.email,
          });
          showMsg(msg, T('auth.ok.welcome') + acc.display + '!', 'success');
          var target =
            acc.role === 'seeker'
              ? 'seeker-dashboard.html'
              : acc.role === 'employer'
                ? 'employer-dashboard.html'
                : 'admin-users.html';
          setTimeout(function () {
            window.location.href = target;
          }, 400);
        } else {
          showMsg(msg, T('auth.err.badLogin'), 'error');
        }
      });
    }

    var regForm = document.getElementById('form-register');
    if (regForm) {
      setRegisterTab('seeker');
      regForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var u = (document.getElementById('reg-user').value || '').trim().toLowerCase();
        var p = (document.getElementById('reg-pass').value || '').trim();
        var email = (document.getElementById('reg-email').value || '').trim() || u + '@users.portal.kz';
        var role = (
          document.getElementById('reg-role-value') || { value: 'seeker' }
        ).value.toLowerCase();
        if (role !== 'seeker' && role !== 'employer') role = 'seeker';
        var companyEl = document.getElementById('reg-company');
        var company = companyEl ? (companyEl.value || '').trim() : '';
        var msg = document.getElementById('auth-messages');
        if (u.length < 2) {
          showMsg(msg, T('auth.err.shortUser'), 'error');
          return;
        }
        if (p.length < 4) {
          showMsg(msg, T('auth.err.shortPass'), 'error');
          return;
        }
        if (ACCOUNTS[u]) {
          showMsg(msg, T('auth.err.taken'), 'error');
          return;
        }
        var display;
        if (role === 'employer') {
          display = company || 'ТОО «' + u + '»';
        } else {
          display = email.split('@')[0].replace(/\./g, ' ');
        }
        JobPortalShell.setUser({
          username: u,
          role: role,
          display: display,
          email: email,
          orgName: role === 'employer' ? company : '',
        });
        showMsg(msg, T('auth.ok.register'), 'success');
        var target = role === 'employer' ? 'employer-dashboard.html' : 'seeker-dashboard.html';
        setTimeout(function () {
          window.location.href = target;
        }, 500);
      });
    }
  });
})();
